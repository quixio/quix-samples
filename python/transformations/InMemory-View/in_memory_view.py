from quixstreaming import ParameterData, QuixStreamingClient, StreamReader,InputTopic, OutputTopic
import pandas as pd
import os
from cross-stream-statefull-processing import CrossStreamStatefullProcessing

class InMemoryView(CrossStreamStatefullProcessing):

    def __init__(self, input_topic: InputTopic, output_topic: OutputTopic):
        super().__init__(input_topic, output_topic)


    def init_state(self):
        self.set_state(pd.DataFrame())


    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, stream_id: str, data: ParameterData):

        data_df = data.to_panda_frame()
        data_df["TAG__streamId"] = stream_id

        df = self.state.append(data_df[["time", "EngineRPM", "TAG__streamId"]) \
                    .groupby("TAG__streamId") \
                    .agg({'time': 'first', 'EngineRPM': 'sum'}) \
                    .reset_index()

        self.set_state(df)

        print(df[["time", "EngineRPM", "TAG__streamId"]])

        self.output_topic.get_or_create_stream("view").parameters.write(df)
            
