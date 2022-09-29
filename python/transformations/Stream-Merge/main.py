from quixstreaming import QuixStreamingClient, StreamEndType, StreamReader, AutoOffsetReset
from quixstreaming.app import App
from quix_function import QuixFunction
import os


# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")

input_topic = client.open_input_topic(os.environ["input"], auto_offset_reset=AutoOffsetReset.Latest)
output_topic = client.open_output_topic(os.environ["output"])


# Callback called for each incoming stream
def read_stream(input_stream: StreamReader):

    quix_function = QuixFunction(input_stream, output_topic)
        
    # React to new data received from input topic.
    input_stream.events.on_read += quix_function.on_event_data_handler
    input_stream.parameters.on_read_pandas += quix_function.on_pandas_frame_handler


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
App.run()