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
    def on_parameter_data_handler(self, data: ParameterData):

        data_df = data.to_panda_frame()

        df = pd.concat([self.state, data_df]) \
            .groupby("TAG__" + self.group_by) \
            .last() \
            .reset_index()

        print(df)
        
        self.set_state(df)
        
