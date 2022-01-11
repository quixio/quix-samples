from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
import pandas as pd
from typing import Union

# Initiate empty df_window
df_window = pd.DataFrame()

class RollingFunction:
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter, parameter_name: str, window: Union[None, int, pd.Timedelta]):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.parameter_name = parameter_name
        self.window = window
    
    # Rolling function to perform
    def rolling_function(self, df: pd.DataFrame, df_window: pd.DataFrame, parameter_name: str):
        # Here we perform the moving average as an example. Other aggregation functions:
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html
        df[parameter_name+'_rolling_avg'] = df_window[parameter_name].agg('mean', axis=0)
        return df

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data.value)

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, df: pd.DataFrame):
        global df_window
        
        # Input dataframe        
        df['time'] = [pd.Timestamp(time_i) for time_i in df['time']]  # Correct time format to pd.Timestamp()
        df_window = df_window.append(df[['time', self.parameter_name]])  # Update df_window

        # Apply window
        if type(self.window) == int:
            df_window = df_window.iloc[-self.window:,:]
        if type(self.window) == pd.Timedelta:
            min_date = df_window['time'].iloc[-1] - self.window
            df_window = df_window[df['time']>min_date]           

        print('Value: ', float(df.loc[0, self.parameter_name]), '. Rolling function: ', df_window[self.parameter_name].mean())

        # Update df with rolling function
        df = self.rolling_function(df, df_window, self.parameter_name)

        # Write data including the new rolling function column
        self.output_stream.parameters.buffer.write(df)  # Send data