import quixstreams as qx
import pandas as pd
import os

pd.set_option('display.max_columns', 10)


class RollingWindow:
    # Initiate
    def __init__(self, stream_consumer: qx.StreamConsumer, stream_producer: qx.StreamProducer):
        self.stream_consumer = stream_consumer
        self.stream_producer = stream_producer

        self.parameter_name = os.environ["ParameterName"]
        if os.environ["WindowType"] == 'Number of Observations':
            self.window = int(os.environ["WindowValue"])
        elif os.environ["WindowType"] == 'Time Period':
            self.window = pd.Timedelta(str(os.environ["WindowValue"]))
        else:
            self.window = None
        self.df_window = pd.DataFrame()

    # Callback triggered for each new parameter data.
    def on_data_frame_handler(self, __: qx.StreamConsumer, df: pd.DataFrame):

        if self.parameter_name not in df.columns:
            return

        # Append latest data to df_window
        self.df_window = pd.concat([self.df_window, df[["timestamp", self.parameter_name]]])

        # Trim out the (now) too old data in the df_window
        if type(self.window) == int:
            self.df_window = self.df_window.iloc[-self.window:, :]
        if type(self.window) == pd.Timedelta:
            min_date = self.df_window['timestamp'].iloc[-1] - self.window.delta
            self.df_window = self.df_window[self.df_window['timestamp'] > min_date]

        # PERFORM A OPERATION ON THE WINDOW
        # Here we perform the moving average as an example. Other aggregation functions:
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html
        df[self.parameter_name + '_rolling_avg'] = self.df_window[self.parameter_name].agg('mean', axis=0)
        print(df[[self.parameter_name, self.parameter_name + '_rolling_avg']])

        # Write data including the new rolling function column
        self.stream_producer.timeseries.buffer.publish(df)  # Send data
