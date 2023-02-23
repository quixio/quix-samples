from quixstreams import QuixStreamingClient, StreamConsumer
from quixstreams.app import App
import os
import pandas as pd

client = QuixStreamingClient()
topic_consumer = client.get_topic_consumer(os.environ["input"], "empty-transformation")
topic_producer = client.get_topic_producer(os.environ["output"])

def on_dataframe_receive(stream_consumer: StreamConsumer, df: pd.DataFrame):
    print(df)

def read_stream(stream_consumer: StreamConsumer):
    stream_consumer.timeseries.on_dataframe_receive = on_dataframe_receive
       
topic_consumer.on_stream_received = read_stream  # we subscribe to data for each stream.

print("Listening to streams. Press CTRL-C to exit.")

App.run() # Handle graceful exit