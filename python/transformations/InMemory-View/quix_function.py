from quixstreaming import ParameterData,InputTopic, StreamReader, OutputTopic
import pandas as pd
from helpers import StatefullProcessing

class QuixFunction(StatefullProcessing):

    def __init__(self, input_topic: InputTopic, input_stream: StreamReader, output_topic: OutputTopic):
        super().__init__(input_topic, input_stream, output_topic)


    def init_state(self):
        self.set_state(pd.DataFrame())


    # Callback triggered for each new parameter data.
    def on_pandas_frame_handler(self, data_df: pd.DataFrame):

        data_df["TAG__streamId"] = self.input_stream.stream_id

        df = self.state.append(data_df[["time", "EngineRPM", "TAG__streamId"]]) \
                    .groupby("TAG__streamId") \
                    .agg({'time': 'first', 'EngineRPM': 'sum'}) \
                    .reset_index()

        self.set_state(df)

        print(df[["time", "EngineRPM", "TAG__streamId"]])

        self.output_topic.get_or_create_stream("view").parameters.write(df)
            