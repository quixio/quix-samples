import quixstreams as qx
from quix_function import QuixFunction
import os

producer_topic: qx.TopicProducer = None


def read_stream(new_stream: qx.StreamConsumer):

    # create the output stream with an ID based on the input stream ID
    stream_producer = producer_topic.create_stream(new_stream.stream_id + "-cleandata-out-stream")

    stream_producer.properties.name = "clean_data"
    stream_producer.properties.location = "/dataset/clean_data"

    buffer_options = qx.TimeseriesBufferConfiguration()
    buffer_options.buffer_timeout = 1000

    buffer = new_stream.timeseries.create_buffer(buffer_options)

    quix_function = QuixFunction(stream_producer)

    # React to new data received from input topic.
    buffer.on_dataframe_released = quix_function.on_dataframe_handler

    # When input stream closes, we close output stream as well.
    def on_stream_close(stream_consumer: qx.StreamConsumer, end_type: qx.StreamEndType):
        stream_producer.close(end_type)
        print("Stream closed:" + stream_producer.stream_id)

    new_stream.on_stream_closed = on_stream_close


def main():
    global producer_topic

    streaming_client = qx.QuixStreamingClient()
    producer_topic = streaming_client.get_topic_producer(os.environ["output"])
    consumer_topic = streaming_client.get_topic_consumer(os.environ["input"])

    consumer_topic.on_stream_received = read_stream

    # Hook up to termination signal (for docker image) and CTRL-C
    print("Listening to streams. Press CTRL-C to exit.")
    qx.App.run()
    print("Exiting")


if __name__ == "__main__":
    main()
    pass
