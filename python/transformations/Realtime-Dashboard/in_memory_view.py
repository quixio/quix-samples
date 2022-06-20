from quixstreaming import ParameterData, InputTopic
import pandas as pd
from helpers import CrossStreamStatefullProcessing
import os

class InMemoryView(CrossStreamStatefullProcessing):

    def __init__(self, input_topic: InputTopic):
        super().__init__(input_topic)

        self.group_by = os.environ["group_by"]


    def init_state(self):
        self.set_state(pd.DataFrame())


    # Callback triggered for each new parameter data.
    def on_pandas_frame_handler(self, data_df: pd.DataFrame):

        df = pd.concat([self.state, data_df]) \
            .groupby("TAG__" + self.group_by) \
            .last() \
            .reset_index()

        print(df)
        
        self.set_state(df)
        
