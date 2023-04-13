import quixstreams as qx
import os
import pickle
import pandas as pd

class CrossStreamStatefullProcessing:

    def __init__(self, consumer_topic: qx.TopicConsumer):
        self.consumer_topic = consumer_topic

        self.state = None

        self.storage_key = "dashboard"

        consumer_topic.on_stream_received = self.read_stream

        self.storage = qx.LocalFileStorage(os.environ["storage_version"])

        consumer_topic.on_committed = self.save_state

        if self.storage.contains_key(self.storage_key):
            print("State loaded.")
            self.state = self.load_state()
        else:
            print("No state found, initializing state.")
            self.init_state()
        
        print("Listening to streams. Press CTRL-C to exit.")

    def init_state(self):
        return

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def load_state(self):
        return pickle.loads(self.storage.get(self.storage_key))

    def save_state(self, topic_consumer: qx.TopicConsumer):
        print("State saved.")
        if self.state is not None:
            self.storage.set("dashboard", pickle.dumps(self.state))

    def read_stream(self, stream_consumer: qx.StreamConsumer):
        print("New stream read:" + stream_consumer.stream_id)
        stream_consumer.timeseries.on_dataframe_received = self.on_dataframe_handler

    def on_dataframe_handler(self, stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
        return
   
    def on_event_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.EventData):
        return
        