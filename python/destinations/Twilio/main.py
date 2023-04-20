import quixstreams as qx
from twilio_sink import TwilioSink
import os

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening input topic")
consumer_topic = client.get_topic_consumer(os.environ["input"])


# read streams
def read_stream(stream_consumer: qx.StreamConsumer):
    print("New stream read:" + stream_consumer.stream_id)

    # handle the data in a function to simplify the example
    twilio_sink = TwilioSink()
    stream_consumer.timeseries.on_dataframe_received = twilio_sink.on_dataframe_handler
    stream_consumer.events.on_data_received = twilio_sink.on_event_data_handler


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the service.
qx.App.run()
