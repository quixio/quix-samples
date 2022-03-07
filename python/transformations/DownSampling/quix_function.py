from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
import pandas as pd


class QuixFunction:
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter):
        self.input_stream = input_stream
        self.output_stream = output_stream

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):
        # Input data frame
        df = data.to_panda_frame()

        # add a date_time column and populate using timestamps
        df['date_time'] = pd.to_datetime(df['time'])

        # this sample uses 100ms of data and down-samples to 10ms
        td = pd.Timedelta(10, "milliseconds")

        # resample and get the mean of the input data
        df = df.set_index('date_time').resample(td).mean().ffill()
        print(df)

        # Send filtered data to output topic
        self.output_stream.parameters.buffer.write(df)

