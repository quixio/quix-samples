from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.models.parametersbufferconfiguration import ParametersBufferConfiguration
from quixstreaming.app import App
from quix_function import QuixFunction
import os
from queue import Queue
from threading import Thread
from queue_helper import insert_from_queue
from postgres_helper import connect_postgres, create_paramdata_table, create_metadata_table, create_eventdata_table, create_properties_table, create_parents_table


# Global Variables
TOPIC = os.environ["input"].replace('-', '_')
TABLE_NAME = {
    "PARAMETER_TABLE_NAME": TOPIC + '_parameter_data',
    "EVENT_TABLE_NAME": TOPIC + '_event_data',
    "METADATA_TABLE_NAME": TOPIC + '_streams_metadata',
    "PROPERTIES_TABLE_NAME": TOPIC + '_streams_properties',
    "PARENTS_TABLE_NAME": TOPIC + '_streams_parents'
}


# Connect to postgres and set up table
try:
    conn = connect_postgres()
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

print("Opening input topic")
input_topic = client.open_input_topic(os.environ["input"])
print(os.environ["input"])

# Initialize Queue
insert_queue = Queue(maxsize=0)

# Create threads that execute insert from Queue
NUM_THREADS = 10

for i in range(NUM_THREADS):
    worker = Thread(target=insert_from_queue, args=(
        conn, TABLE_NAME["PARAMETER_TABLE_NAME"], insert_queue, 0.25, 50))
    # Thread will be killed when main thread is terminated
    worker.setDaemon(True)
    worker.start()


# read streams
def read_stream(input_stream: StreamReader):
    print("New stream read:" + input_stream.stream_id)

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
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit
App.run()
