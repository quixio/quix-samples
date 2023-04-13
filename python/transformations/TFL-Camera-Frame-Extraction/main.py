import quixstreams as qx
from quix_function import QuixFunction
import os


# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")

consumer_topic = client.get_topic_consumer(os.environ["input"], auto_offset_reset = qx.AutoOffsetReset.Latest)
producer_topic = client.get_topic_producer(os.environ["output"])


# Callback called for each incoming stream
def read_stream(stream_consumer: qx.StreamConsumer):

    # Create a new stream to output data
    stream_producer = producer_topic.create_stream(stream_consumer.stream_id)
    stream_producer.properties.parents.append(stream_consumer.stream_id)

    # handle the data in a function to simplify the example
    quix_function = QuixFunction(stream_consumer, stream_producer)
        
    # React to new data received from input topic.
    stream_consumer.events.on_data_received = quix_function.on_event_data_handler
    stream_consumer.timeseries.on_dataframe_received = quix_function.on_dataframe_handler

    # When input stream closes, we close output stream as well. 
    def on_stream_close(stream_consumer: qx.StreamConsumer, endType: qx.StreamEndType):
        stream_producer.close()
        print("Stream closed:" + stream_producer.stream_id)

    stream_consumer.on_stream_closed = on_stream_close

# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
qx.App.run()