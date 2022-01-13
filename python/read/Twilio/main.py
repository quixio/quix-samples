from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.app import App
from twilio_sink import TwilioSink
import os

# Create a client to help you to create input reader or output writer for specified topic.
client = QuixStreamingClient('{placeholder:token}')
client.api_url = "https://portal-api.dev.quix.ai"

print("Opening input topic")
input_topic = client.open_input_topic(os.environ["input"])


# read streams
def read_stream(input_stream: StreamReader):
    print("New stream read:" + input_stream.stream_id)

    # handle the data in a function to simplify the example
    twilio_sink = TwilioSink()
    input_stream.parameters.on_read += twilio_sink.on_parameter_data_handler
    input_stream.events.on_read += twilio_sink.on_parameter_data_handler


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the service.
App.run()
