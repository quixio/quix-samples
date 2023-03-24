import quixstreams as qx
from quix_function import QuixFunction
import os


# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening input and output topics")
consumer_topic = client.get_topic_consumer(os.environ["input"], "default-consumer-group")
producer_topic = client.get_topic_producer(os.environ["output"])


# Callback called for each incoming stream
def read_stream(consumer_stream: qx.StreamConsumer):

    # Create a new stream to output data
    producer_stream = producer_topic.get_or_create_stream(consumer_stream.stream_id + "-rss-filtering")
    producer_stream.properties.parents.append(consumer_stream.stream_id)

    # handle the data in a function to simplify the example
    quix_function = QuixFunction(consumer_stream, producer_stream)
        
    # React to new data received from input topic.
    consumer_stream.timeseries.on_data_received = quix_function.on_data_handler

    # When input stream closes, we close output stream as well. 
    def on_stream_close():
        producer_stream.close()
        print("Stream closed:" + producer_stream.stream_id)

    consumer_stream.on_stream_closed = on_stream_close


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
qx.App.run()
