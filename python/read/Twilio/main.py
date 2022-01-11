from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.app import App
from twilio_sink import TwilioSink
from twilio.rest import Client
import os

# Create a client to help you to create input reader or output writer for specified topic.
client = QuixStreamingClient('{placeholder:token}')

print("Opening input topic")
input_topic = client.open_input_topic(os.environ["input"])

# read streams
def read_stream(input_stream: StreamReader):
    print("New stream read:" + input_stream.stream_id)

    # handle the data in a function to simplify the example
    quix_function = TwilioSink()
    input_stream.parameters.on_read += quix_function.on_parameter_data_handler
    input_stream.events.on_read += quix_function.on_parameter_data_handler


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
App.run()
