from quixstreaming import ParameterData, InputTopic
import pandas as pd
from cross_stream_statefull_processing import CrossStreamStatefullProcessing

class InMemoryView(CrossStreamStatefullProcessing):

    def __init__(self, input_topic: InputTopic):
        super().__init__(input_topic)


    def init_state(self):
        self.set_state(pd.DataFrame())


    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):

        data_df = data.to_panda_frame()

        df = pd.concat([self.state, data_df]) \
            .groupby("TAG__rider") \
            .last() \
            .reset_index()
        
        self.set_state(df)
        
