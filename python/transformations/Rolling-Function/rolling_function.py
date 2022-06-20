from quixstreaming import StreamReader, StreamWriter
from rolling_window import RollingWindow
import pandas as pd
import os


class RollingFunction:
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter):
        self.input_stream = input_stream
        self.output_stream = output_stream

        self.parameter_name = str(os.environ["ParameterName"])
        self.rolling_window = RollingWindow(os.environ["WindowType"], os.environ["WindowValue"])

    # Callback triggered for each new parameter data.
    def on_pandas_frame_handler(self, df: pd.DataFrame):

        df['time'] = df['time'].apply(lambda x: pd.Timestamp(x))   # Correct time format to pd.Timestamp()

        if self.parameter_name in df:
            self.rolling_window.append(df[['time', self.parameter_name]])

            # Here we perform the moving average as an example. Other aggregation functions:
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html
            df[self.parameter_name + '_rolling_avg'] = self.rolling_window.df_window[self.parameter_name].agg('mean', axis=0)
            
            print(df[[self.parameter_name, self.parameter_name + '_rolling_avg']])

            # Write data including the new rolling function column
            self.output_stream.parameters.buffer.write(df)  # Send data