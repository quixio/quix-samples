import quixstreams as qx
from quix_function import QuixFunction
import os


# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening input and output topics")
consumer_topic = client.get_topic_consumer(os.environ["input"], "default-consumer-group-5")

webhook_url = os.environ["webhook_url"]

# Callback called for each incoming stream
def read_stream(stream_consumer: qx.StreamConsumer):

    # Create a new stream to output data
    # handle the data in a function to simplify the example
    quix_function = QuixFunction(webhook_url, stream_consumer)
        
    # React to new data received from input topic.
    stream_consumer.timeseries.on_dataframe_received = quix_function.on_dataframe_handler
    stream_consumer.events.on_data_received = quix_function.on_event_data_handler

# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
qx.App.run()