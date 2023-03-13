import quixstreams as qx
import os
import pickle
import pandas as pd

class StatefulProcessing:
    def __init__(self, consumer_topic: qx.topicconsumer, consumer_stream: qx.streamconsumer, producer_topic: qx.topicproducer):
        self.input_stream = consumer_stream
        self.output_topic = producer_topic

        self.state = None

        self.storage_key = os.environ["storage_version"]

        self.storage = qx.LocalFileStorage(os.environ["storage_version"])

        consumer_topic.on_committed += self.save_state

        if self.storage.containsKey(self.storage_key):
            print("State loaded.")
            self.state = self.load_state()
        else:
            print("No state found, initializing state.")
            self.init_state()

    def init_state(self):
        return

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def load_state(self):
        return pickle.loads(self.storage.get(self.storage_key))

    def save_state(self):
        print("State saved.")
        if self.state is not None:
            self.storage.set("dashboard", pickle.dumps(self.state))

     # Callback triggered for each new parameter data.
    def on_pandas_frame_handler(self, df: pd.DataFrame):
        return


        