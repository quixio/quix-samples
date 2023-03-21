import quixstreams as qx
from quix_function import QuixFunction
import os


# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")

print("Opening input and output topics")
consumer_topic = client.get_topic_consumer(os.environ["input"], "default-consumer-group",
                                           auto_offset_reset=qx.AutoOffsetReset.Latest)
producer_topic = client.get_topic_producer(os.environ["output"])


# Callback called for each incoming stream
def read_stream(consumer_stream: qx.StreamConsumer):

    quix_function = QuixFunction(consumer_topic, producer_topic)
        
    # React to new data received from input topic.
    consumer_stream.events.on_read = quix_function.on_event_data_handler
    consumer_stream.timeseries.on_dataframe_received = quix_function.on_pandas_frame_handler


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
qx.App.run()
