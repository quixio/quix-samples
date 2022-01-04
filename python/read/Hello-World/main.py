from quixstreaming import StreamingClient, ParameterData, StreamReader
from quixstreaming.models.parametersbufferconfiguration import ParametersBufferConfiguration
import signal
import threading
import time

# Create a client to help you to create input reader or output writer for specified topic.
client = QuixStreamingClient('{placeholder:token}')

input_topic = client.open_input_topic('{placeholder:input}')


# read streams
def read_stream(new_stream: StreamReader):
    print("New stream read:" + new_stream.stream_id)

    buffer_options = ParametersBufferConfiguration()
    buffer_options.time_span_in_milliseconds = 100

    buffer = new_stream.parameters.create_buffer(buffer_options)

    def on_parameter_data_handler(data: ParameterData):
        # print first value of ParameterA parameter if it exists
        hello_world_value = data.timestamps[0].parameters['ParameterA'].numeric_value
        if hello_world_value is not None:
            print("ParameterA - " + str(data.timestamps[0]) + ": " + str(hello_world_value))

    buffer.on_read += on_parameter_data_handler


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream
input_topic.start_reading()  # initiate read

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
event = threading.Event()


def signal_handler(sig, frame):
    # dispose the topic(s) and close the stream(s)
    input_topic.dispose()

    print("Setting termination flag")
    event.set()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while not event.is_set():
    time.sleep(1)

print("Exiting")
