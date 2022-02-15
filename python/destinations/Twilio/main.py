from quixstreaming import QuixStreamingClient, StreamReader
from quixstreaming.app import App
from twilio_sink import TwilioSink
import os

# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

print("Opening input topic")
input_topic = client.open_input_topic(os.environ["input"])


# read streams
def read_stream(input_stream: StreamReader):
    print("New stream read:" + input_stream.stream_id)

    # handle the data in a function to simplify the example
    twilio_sink = TwilioSink()
    input_stream.parameters.on_read += twilio_sink.on_parameter_data_handler
    input_stream.events.on_read += twilio_sink.on_event_data_handler


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the service.
App.run()
