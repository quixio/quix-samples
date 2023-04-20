import quixstreams as qx
from quix_function import QuixFunction
import os
from setup_logger import logger
from queue import Queue
from threading import Thread
from queue_helper import consume_queue, stop
from postgres_helper import connect_postgres, create_paramdata_table, create_metadata_table, create_eventdata_table, create_properties_table, create_parents_table, create_schema


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
CONSUMER_GROUP = "postgres_sink"


# Connect to postgres and set up table
try:
    conn = connect_postgres()
    logger.info("CONNECTED!")
except Exception as e:
    logger.info(f"ERROR!: {e}")
    raise

# Creata table if it doesn't exist
create_schema(conn)
create_paramdata_table(conn, TABLE_NAME["PARAMETER_TABLE_NAME"])
create_metadata_table(conn, TABLE_NAME["METADATA_TABLE_NAME"])
create_eventdata_table(conn, TABLE_NAME["EVENT_TABLE_NAME"])
create_parents_table(conn, TABLE_NAME["PARENTS_TABLE_NAME"])
create_properties_table(conn, TABLE_NAME["PROPERTIES_TABLE_NAME"])


# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

logger.info("Opening input topic")
consumer_topic = client.get_topic_consumer(os.environ["input"], CONSUMER_GROUP)
logger.info(os.environ["input"])

# Initialize Queue
param_insert_queue = Queue(maxsize = MAX_QUEUE_SIZE)
event_insert_queue = Queue(maxsize = MAX_QUEUE_SIZE)
insert_queue = (param_insert_queue, event_insert_queue)

# Create threads that execute insert from Queue
NUM_THREADS = 1
WAIT_INTERVAL = 0.25 # Seconds
BATCH_SIZE = 50

for i in range(NUM_THREADS):
    worker = Thread(target = consume_queue, args=(
        conn, TABLE_NAME["PARAMETER_TABLE_NAME"], param_insert_queue, WAIT_INTERVAL, BATCH_SIZE))
    # Thread will be killed when main thread is terminated
    worker.setDaemon(True)
    worker.start()

for i in range(NUM_THREADS):
    worker = Thread(target = consume_queue, args=(
        conn, TABLE_NAME["EVENT_TABLE_NAME"], event_insert_queue, WAIT_INTERVAL, BATCH_SIZE))
    # Thread will be killed when main thread is terminated
    worker.setDaemon(True)
    worker.start()


# read streams
def read_stream(stream_consumer: qx.StreamConsumer):
    logger.info("New stream read:" + stream_consumer.stream_id)

    buffer_options = qx.TimeseriesBufferConfiguration()
    buffer_options.time_span_in_milliseconds = 100

    buffer = stream_consumer.timeseries.create_buffer(buffer_options)

    # handle the data in a function to simplify the example
    quix_function = QuixFunction(conn, TABLE_NAME, insert_queue, stream_consumer)

    buffer.on_data_released = quix_function.on_data_handler
    stream_consumer.events.on_data_received = quix_function.on_event_data_handler

    stream_consumer.properties.on_changed = quix_function.on_stream_properties_changed
    stream_consumer.on_stream_closed = quix_function.on_stream_closed
    stream_consumer.timeseries.on_definitions_changed = quix_function.on_parameter_definition_changed

    consumer_topic.on_committing = quix_function.on_committing


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
logger.info("Listening to streams. Press CTRL-C to exit.")

def before_shutdown():
    stop()

# Handle graceful exit
qx.App.run(before_shutdown=before_shutdown)