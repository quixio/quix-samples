from quixstreaming import ParameterData, EventData, StreamEndType, StreamReader

import os
from queue import Queue

from postgres_helper import create_column, insert_row, delete_row, Null

class QuixFunction:

    def __init__(self, conn, table_name, insert_queue: Queue, input_stream: StreamReader):
        self.conn = conn
        self.table_name = table_name
        self.insert_queue = insert_queue
        self.input_stream = input_stream
        self.data_start = Null()
        self.data_end = Null()
        self.insert_parents()
        self.topic = os.environ["input"].replace('-', '_')
        self.committing = False

    def on_committing(self):
        print("on_committing")
        self.committing = True

    def reset_data_ts(self):
        self.data_start = Null()
        self.data_end = Null()

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):

        for ts in data.timestamps:
            row = {'timestamp': ts.timestamp_nanoseconds}
            if type(self.data_start) == Null:
                self.data_start = ts.timestamp_nanoseconds
                self.data_end = ts.timestamp_nanoseconds
            self.data_start = min(self.data_start, ts.timestamp_nanoseconds)
            self.data_end = max(self.data_end, ts.timestamp_nanoseconds)

            for k, v in ts.tags.items():
                row['TAG_' + k] = v

            for k, v in ts.parameters.items():
                if v.numeric_value:
                    row[k + '_n'] = v.numeric_value

                if v.string_value:
                    row[k + '_s'] = v.string_value

            # Add to Queue
            if not self.committing:
                self.insert_queue.put(row, block=True)

            if self.insert_queue.qsize() == 0 and self.committing == True:
                self.committing = False
                print("Commit success!")

    def insert_metadata(self):
        cols = []
        vals = []
        for k, v in self.input_stream.properties.metadata.items():
            create_column(
                self.conn, self.table_name["METADATA_TABLE_NAME"], k, 'STRING')
            cols.append(k)
            vals.append(v)
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
        cols = ["name", "location", "topic",
                "status", "data_start", "data_end"]
        vals = [self.input_stream.properties.name, self.input_stream.properties.location,
                self.topic, status, self.data_start, self.data_end]
        insert_row(
            self.conn, self.table_name["PROPERTIES_TABLE_NAME"], cols, [vals])

    def on_event_data_handler(self, data: EventData):
        print("on_event_data_handler")

        row = {'timestamp': data.timestamp_nanoseconds}

        for k, v in data.tags.items():
            create_column(
                self.conn, self.table_name["EVENT_TABLE_NAME"], 'TAG_' + k, 'STRING')
            row['TAG_' + k] = v

        row['value'] = data.value
        insert_row(self.conn, self.table_name["EVENT_TABLE_NAME"], list(
            row.keys()), [list(row.values())])

    def on_stream_properties_changed(self):
        print("on_stream_properties_changed")
        self.insert_metadata()
        self.insert_properties("open")
        # Reset data start and end
        self.reset_data_ts()

        self.update_parents()

    def on_parameter_definition_changed(self):
        print("on_parameter_definition_changed")
        self.insert_metadata()
        self.insert_properties("open")
        # Reset data start and end
        self.reset_data_ts()

        self.update_parents()

    def on_stream_closed(self, data: StreamEndType):
        print("on_stream_closed")
        self.insert_properties(str(data))
