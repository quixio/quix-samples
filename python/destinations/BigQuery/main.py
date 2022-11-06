from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.models.parametersbufferconfiguration import ParametersBufferConfiguration
from quixstreaming.app import App
from quix_function import QuixFunction
import os
from setup_logger import logger
from queue import Queue
from threading import Thread
from queue_helper import consume_queue
from bigquery_helper import connect_bigquery, create_paramdata_table, create_metadata_table, create_eventdata_table, create_properties_table, create_parents_table


# Global Variables
TOPIC = os.environ["input"].replace('-', '_')
TABLE_NAME = {
    "PARAMETER_TABLE_NAME": TOPIC + '_parameter_data',
    "EVENT_TABLE_NAME": TOPIC + '_event_data',
    "METADATA_TABLE_NAME": TOPIC + '_streams_metadata',
    "PROPERTIES_TABLE_NAME": TOPIC + '_streams_properties',
    "PARENTS_TABLE_NAME": TOPIC + '_streams_parents'
}
MAX_QUEUE_SIZE = int(os.environ["MAX_QUEUE_SIZE"])

# Connect to postgres and set up table
try:
    conn = connect_bigquery()
    logger.info("CONNECTED!")
except:
    # End program or something
    pass

# Creata table if it doesn't exist
create_paramdata_table(conn, TABLE_NAME["PARAMETER_TABLE_NAME"])
create_metadata_table(conn, TABLE_NAME["METADATA_TABLE_NAME"])
create_eventdata_table(conn, TABLE_NAME["EVENT_TABLE_NAME"])
create_parents_table(conn, TABLE_NAME["PARENTS_TABLE_NAME"])
create_properties_table(conn, TABLE_NAME["PROPERTIES_TABLE_NAME"])


# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

logger.info("Opening input topic")
input_topic = client.open_input_topic(os.environ["input"])
logger.info(os.environ["input"])

# Initialize Queue
param_insert_queue = Queue(maxsize=MAX_QUEUE_SIZE)
event_insert_queue = Queue(maxsize=MAX_QUEUE_SIZE)
insert_queue = (param_insert_queue, event_insert_queue)

# Create threads that execute insert from Queue
NUM_THREADS = 1
WAIT_INTERVAL = 0.25 # Seconds
BATCH_SIZE = 50

for i in range(NUM_THREADS):
    worker = Thread(target=consume_queue, args=(
        conn, TABLE_NAME["PARAMETER_TABLE_NAME"], param_insert_queue, WAIT_INTERVAL, BATCH_SIZE))
    # Thread will be killed when main thread is terminated
    worker.setDaemon(True)
    worker.start()

for i in range(NUM_THREADS):
    worker = Thread(target=consume_queue, args=(
        conn, TABLE_NAME["EVENT_TABLE_NAME"], event_insert_queue, WAIT_INTERVAL, BATCH_SIZE))
    # Thread will be killed when main thread is terminated
    worker.setDaemon(True)
    worker.start()


# read streams
def read_stream(input_stream: StreamReader):
    logger.info("New stream read:" + input_stream.stream_id)

    buffer_options = ParametersBufferConfiguration()
    buffer_options.time_span_in_milliseconds = 100

    buffer = input_stream.parameters.create_buffer(buffer_options)

    # handle the data in a function to simplify the example
    quix_function = QuixFunction(conn, TABLE_NAME, insert_queue, input_stream)

    buffer.on_read += quix_function.on_parameter_data_handler
    input_stream.events.on_read += quix_function.on_event_data_handler

    input_stream.properties.on_changed += quix_function.on_stream_properties_changed
    input_stream.on_stream_closed += quix_function.on_stream_closed
    input_stream.parameters.on_definitions_changed += quix_function.on_parameter_definition_changed

    input_topic.on_committing += quix_function.on_committing


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

# Hook up to termination signal (for docker image) and CTRL-C
logger.info("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
App.run()
