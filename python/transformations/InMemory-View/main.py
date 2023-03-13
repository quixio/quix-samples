import quixstreams as qx
import pandas as pd
from helpers import StatefulProcessing
import os


# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening input and output topics")

# Change consumer group to a different constant if you want to run model locally.
consumer_topic = client.get_topic_consumer(os.environ["input"], consumer_group = "view")
producer_topic = client.get_topic_producer(os.environ["output"])


# callback for each incoming stream
def read_stream(consumer_stream: qx.StreamConsumer):

    # initialize the state helper
    state = StatefulProcessing(consumer_topic=consumer_topic, consumer_stream=consumer_stream, producer_topic=producer_topic)

    # set the initial state
    state.set_state(pd.DataFrame())

    # callback for each incoming DataFrame
    def on_pandas_frame_handler(data_df: pd.DataFrame):
        # tag the data with the stream_id it originates from
        # this can be used for grouping later
        data_df["TAG__streamId"] = consumer_stream.stream_id

        df = state.append(data_df[["time", "EngineRPM", "TAG__streamId"]]) \
            .groupby("TAG__streamId") \
            .agg({'time': 'first', 'EngineRPM': 'sum'}) \
            .reset_index()

        state.set_state(df)

        print(df[["time", "EngineRPM", "TAG__streamId"]])

        producer_topic.get_or_create_stream("view").timeseries.publish(df)

    # React to new data
    consumer_stream.timeseries.on_read_pandas = on_pandas_frame_handler


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
qx.App.run()
