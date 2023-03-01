import quixstreams as qx
import os
import pandas as pd


client = qx.QuixStreamingClient()

topic_consumer = client.get_topic_consumer(topic_id_or_name = os.environ["input"],
                                           consumer_group = "empty-transformation")
topic_producer = client.get_topic_producer(topic_id_or_name = os.environ["output"])


def on_dataframe_received_handler(stream_consumer: qx.StreamConsumer, df: pd.DataFrame):

    # publish the DataFrame to the producer stream
    # or change this code to process the data in any way to
    # pass on the result of a transformation, ML model or other logic.
    # set the output stream id to the same as the input stream
    stream_producer = topic_producer.get_or_create_stream(stream_id = stream_consumer.stream_id)

    # publish the DataFrame using the timeseries buffer
    stream_producer.timeseries \
        .buffer \
        .publish(df)


def on_stream_received_handler(stream_consumer: qx.StreamConsumer):
    # subscribe to new DataFrames being received
    # if you aren't familiar with DataFrames there are other callbacks available
    # refer to the docs here: https://docs.quix.io/sdk/subscribe.html
    stream_consumer.timeseries.on_dataframe_received = on_dataframe_received_handler


# subscribe to new streams being received
topic_consumer.on_stream_received = on_stream_received_handler

print("Listening to streams. Press CTRL-C to exit.")

# Handle termination signals and provide a graceful exit
qx.App.run()
