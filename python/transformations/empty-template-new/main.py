#from quixstreams import QuixStreamingClient, StreamConsumer, App
import quixstreams as qx
import os
import pandas as pd

client = qx.QuixStreamingClient()
topic_consumer = client.get_topic_consumer(os.environ["input"], "empty-transformation")
topic_producer = client.get_topic_producer(os.environ["output"])

def on_dataframe_received_handler(stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
    print(df)

def on_stream_received_handler(stream_consumer: qx.StreamConsumer):
    stream_consumer.timeseries.on_dataframe_received = on_dataframe_received_handler
       
topic_consumer.on_stream_received = on_stream_received_handler  # we subscribe to data for each stream.

print("Listening to streams. Press CTRL-C to exit.")

App.run() # Handle graceful exit