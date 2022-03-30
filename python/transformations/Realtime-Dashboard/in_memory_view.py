from quixstreaming import ParameterData, QuixStreamingClient, StreamReader,InputTopic, OutputTopic
import pandas as pd
import os
from cross-stream-statefull-processing import CrossStreamStatefullProcessing

class InMemoryView(CrossStreamStatefullProcessing):

    def __init__(self, input_topic: InputTopic, output_topic: OutputTopic):
        super().__init__(input_topic, output_topic)
        self.parameters = os.environ["parameters"].split(",")
        self.group_by = os.environ["group_by"]

    def init_state(self):
        self.set_state(pd.DataFrame())


    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):

        data_df = data.to_panda_frame()

        print(data_df.columns)

        aggregation = {'time': 'first'}

        for parameter in self.parameters:
            aggregation[parameter] = sum

        if all(item in self.parameters for item in data_df.columns):
            df = self.state.append(data_df[["time"] + self.parameters + ["TAG__" + self.group_by]]) \
                        .groupby(self.group_by) \
                        .agg(aggregation) \
                        .reset_index()

            self.set_state(df)

            print(df[["time"] + self.parameter + ["TAG__" + self.group_by]]])

            self.output_topic.get_or_create_stream("view").parameters.write(df)
            
