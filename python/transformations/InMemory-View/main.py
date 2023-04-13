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

# initialize the state helper
state_helper = StatefulProcessing(consumer_topic = consumer_topic, producer_topic = producer_topic)

# callback for each incoming DataFrame
def on_dataframe_received_handler(stream_consumer: qx.StreamConsumer, data_df: pd.DataFrame):
    # tag the data with the stream_id it originates from
    # this can be used for grouping later
    data_df["TAG__streamId"] = stream_consumer.stream_id

    state_value = state_helper.get_state()

    df = state_value.append(data_df[["timestamp", "EngineRPM", "TAG__streamId"]]) \
        .groupby("TAG__streamId") \
        .agg({'timestamp': 'first', 'EngineRPM': 'sum'}) \
        .reset_index()

    state_helper.set_state(df)

    print(df[["timestamp", "EngineRPM", "TAG__streamId"]])

    producer_topic.get_or_create_stream("view").timeseries.publish(df)


# callback for each incoming stream
def read_stream(consumer_stream: qx.StreamConsumer):
    global state_helper

    # set the initial state
    state_helper.set_state(pd.DataFrame())

    # React to new data
    consumer_stream.timeseries.on_dataframe_received = on_dataframe_received_handler


# Hook up events before initiating read to avoid losing out on any data
consumer_topic.on_stream_received = read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
qx.App.run()
