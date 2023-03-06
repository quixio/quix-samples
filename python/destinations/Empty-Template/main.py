import quixstreams as qx
import os
import pandas as pd


client = qx.QuixStreamingClient()

# get the topic consumer for a specific consumer group
topic_consumer = client.get_topic_consumer(topic_id_or_name = os.environ["input"],
                                           consumer_group = "empty-destination")


def on_dataframe_received_handler(stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
    # do something with the data here
    print(df)


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
