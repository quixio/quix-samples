import quixstreams as qx
from quix_function import QuixFunction
import os

PREDICT_STREAM_NAME = "predict_data"
PREDICT_STREAM_PATH = "/dataset/predict_data"
PREDICT_STREAM_ID = "-predict-out-stream"

producer_topic = None


def read_stream(new_stream: qx.StreamConsumer):
    stream_producer = producer_topic.create_stream(new_stream.stream_id + PREDICT_STREAM_ID)

    stream_producer.properties.name = PREDICT_STREAM_NAME
    stream_producer.properties.location = PREDICT_STREAM_PATH

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

    streamingclient = qx.QuixStreamingClient()

    consumer_topic = streamingClient.get_topic_consumer(os.environ["input"])
    producer_topic = streamingClient.get_topic_producer(os.environ["output"])

    # Hook up events before initiating read to avoid losing out on any data
    consumer_topic.on_stream_received = read_stream

    # Hook up to termination signal (for docker image) and CTRL-C
    print("Listening to streams. Press CTRL-C to exit.")
    qx.App.run()
    print("Exiting")


if __name__ == "__main__":
    main()
    pass
