import quixstreams as qx
from threshold_function import ThresholdAlert
import os
import traceback


# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# Change consumer group to a different constant if you want to run model locally.
print("Opening input and output topics")

# Environment variables
consumer_topic = client.get_topic_consumer(os.environ["input"], "default-consumer-group")
producer_topic = client.get_topic_producer(os.environ["output"])

try:
    bufferMilliSeconds = os.environ["bufferMilliSeconds"]
    msecs = int(bufferMilliSeconds)
except ValueError:
    print("bufferMilliSeconds should be an integer. ERROR: {}".format(traceback.format_exc()))


# Callback called for each incoming stream
def read_stream(consumer_stream: qx.StreamConsumer):
    # Create a new stream to output data
    producer_stream = producer_topic.get_or_create_stream(consumer_stream.stream_id + '-' + os.environ["Quix__Deployment__Name"])
    producer_stream.properties.parents.append(consumer_stream.stream_id)

    # handle the data in a function to simplify the example
    quix_function = ThresholdAlert(producer_stream)

    buffer_options = qx.TimeseriesBufferConfiguration()
    buffer_options.time_span_in_milliseconds = msecs
    buffer = consumer_stream.timeseries.create_buffer()

    # React to new data received from input topic.
    buffer.on_dataframe_released = quix_function.on_pandas_frame_handler

    # When input stream closes, we close output stream as well.
    def on_stream_close(stream_consumer: qx.StreamConsumer, end_type: qx.StreamEndType):
        producer_stream.close()
        print("Stream closed:" + producer_stream.stream_id)

    consumer_stream.on_stream_closed = on_stream_close


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
qx.App.run()
