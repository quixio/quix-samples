from quixstreaming import ParameterData, EventData, StreamEndType, StreamReader

import os
from queue import Queue
from threading import Lock
from setup_logger import logger
from utils import format_nanoseconds
from timescale_helper import create_column, insert_row, delete_row, Null
import re



class QuixFunction:

    def __init__(self, conn, table_name, insert_queue: Queue, input_stream: StreamReader):
        self.conn = conn
        self.table_name = table_name
        self.param_insert_queue = insert_queue[0]
        self.event_insert_queue = insert_queue[1]
        self.input_stream = input_stream
        self.data_start = Null()
        self.data_end = Null()
        self.insert_parents()
        self.topic = os.environ["input"].replace('-', '_')
        self.mutex = Lock()

    def on_committing(self):
        logger.debug("on_committing")
        self.mutex.acquire()
        logger.debug("on_committing entered")
        
        self.param_insert_queue.join()
        self.event_insert_queue.join()
        self.mutex.release()
        logger.debug("on_committing done")


    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):

        self.mutex.acquire()

        for ts in data.timestamps:
            row = {'timestamp': format_nanoseconds(ts.timestamp_nanoseconds), 'stream_id': self.input_stream.stream_id}
            if type(self.data_start) == Null:
                self.data_start = ts.timestamp_nanoseconds
                self.data_end = ts.timestamp_nanoseconds
            self.data_start = min(self.data_start, ts.timestamp_nanoseconds)
            self.data_end = max(self.data_end, ts.timestamp_nanoseconds)

            for k, v in ts.tags.items():
                k = re.sub('[^0-9a-zA-Z]+', '_', k)
                row['TAG_' + k] = v

            for k, v in ts.parameters.items():
                k = re.sub('[^0-9a-zA-Z]+', '_', k)
                if v.numeric_value:
                    row[k + '_n'] = v.numeric_value

                if v.string_value:
                    row[k + '_s'] = v.string_value

            # Add to Queue
            self.param_insert_queue.put(row, block=True)

        self.mutex.release()

    def insert_metadata(self):
        cols = ["stream_id"]
        vals = [self.input_stream.stream_id]
        for k, v in self.input_stream.properties.metadata.items():
            k = re.sub('[^0-9a-zA-Z]+', '_', k)
            create_column(
                self.conn, self.table_name["METADATA_TABLE_NAME"], k, 'STRING')
            cols.append(k)
            vals.append(v)
        if len(vals) > 0:
            insert_row(
                self.conn, self.table_name["METADATA_TABLE_NAME"], cols, [vals])

    def insert_parents(self):
        for parent in self.input_stream.properties.parents:
            cols = ['stream_id', 'parent_id']
            vals = [self.input_stream.stream_id, parent]
            insert_row(
                self.conn, self.table_name["PARENTS_TABLE_NAME"], cols, [vals])

    def update_parents(self):
        delete_row(self.conn, self.table_name["PARENTS_TABLE_NAME"],
                   f"stream_id = '{self.input_stream.stream_id}'")
        self.insert_parents()

    def insert_properties(self, status: str):
        status_map = {
            "open": "open",
            "StreamEndType.Closed": "closed",
            "StreamEndType.Aborted": "aborted",
            "StreamEndType.Terminated": "terminated"
        }

        cols = ["topic", "status", "stream_id"]
        vals = [self.topic, status_map[status], self.input_stream.stream_id]

        if self.input_stream.properties.name is not None:
            cols.append("name")
            vals.append(self.input_stream.properties.name)

        if self.input_stream.properties.location is not None:
            cols.append("location")
            vals.append(self.input_stream.properties.location)

        if type(self.data_start) != Null:
            cols.append("data_start")
            cols.append("data_end")
            vals.append(self.data_start)
            vals.append(self.data_end)

        insert_row(
            self.conn, self.table_name["PROPERTIES_TABLE_NAME"], cols, [vals])

    def on_event_data_handler(self, data: EventData):
        logger.debug("on_event_data_handler")

        row = {'timestamp': format_nanoseconds(data.timestamp_nanoseconds), 'stream_id': self.input_stream.stream_id}

        for k, v in data.tags.items():
            k = re.sub('[^0-9a-zA-Z]+', '_', k)
            create_column(
                self.conn, self.table_name["EVENT_TABLE_NAME"], 'TAG_' + k, 'STRING')
            row['TAG_' + k] = v

        row['value'] = data.value
        self.event_insert_queue.put(row, block=True)


    def on_stream_properties_changed(self):
        logger.debug("on_stream_properties_changed")
        self.insert_metadata()
        self.insert_properties("open")
        self.update_parents()

    def on_parameter_definition_changed(self):
        logger.debug("on_parameter_definition_changed")
        self.insert_metadata()
        self.insert_properties("open")
        self.update_parents()

    def on_stream_closed(self, data: StreamEndType):
        logger.debug("on_stream_closed")
        self.insert_properties(str(data))