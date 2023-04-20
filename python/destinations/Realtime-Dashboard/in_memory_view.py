import quixstreams as qx
import pandas as pd
from helpers import CrossStreamStatefullProcessing


class InMemoryView(CrossStreamStatefullProcessing):

    def __init__(self, consumer_topic: qx.TopicConsumer):
        super().__init__(consumer_topic)

    def init_state(self):
        self.set_state(pd.DataFrame())


    # Callback triggered for each new parameter data.
    def on_dataframe_handler(self, stream_consumer: qx.StreamConsumer, data_df: pd.DataFrame):

        print(data_df)
        
        self.set_state(data_df)
        