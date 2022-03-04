from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
import pandas as pd
import os


class RollingFunction:
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter):
        self.input_stream = input_stream
        self.output_stream = output_stream

        self.parameter_name = str(os.environ["ParameterName"])
        self.df_window = pd.DataFrame()
        
        # Define window out of WindowType and WindowValue environmental variables
        if os.environ["WindowType"] == 'Number of Observations':
            self.window = int(os.environ["WindowValue"])
        elif os.environ["WindowType"] == 'Time Period':
            self.window = pd.Timedelta(str(os.environ["WindowValue"]))
        else:
            self.window = None

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data.value)

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, df: pd.DataFrame):

        if self.parameter_name in df:
            # Input dataframe        
            df['time'] = [pd.Timestamp(time_i) for time_i in df['time']]  # Correct time format to pd.Timestamp()
            self.df_window = self.df_window.append(df[['time', self.parameter_name]])  # Update df_window

            # Apply window
            if type(self.window) == int:
                self.df_window = self.df_window.iloc[-self.window:, :]
            if type(self.window) == pd.Timedelta:
                min_date = self.df_window['time'].iloc[-1] - self.window
                self.df_window = self.df_window[self.df_window['time'] > min_date]

            print('Value: ', float(df.loc[0, self.parameter_name]),
                '. Rolling function: ', self.df_window[self.parameter_name].mean())

            # Update df with rolling function
            df = self._rolling_function(df)

            # Write data including the new rolling function column
            self.output_stream.parameters.buffer.write(df)  # Send data

    # Rolling function to perform
    def _rolling_function(self, df: pd.DataFrame):
        # Here we perform the moving average as an example. Other aggregation functions:
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html
        df[self.parameter_name + '_rolling_avg'] = self.df_window[self.parameter_name].agg('mean', axis=0)
        return df
