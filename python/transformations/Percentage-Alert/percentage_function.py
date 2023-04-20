import quixstreams as qx
import pandas as pd
import os

pd.set_option('display.max_columns', 10)


class PercentageAlert:
    # Initiate
    def __init__(self, stream_consumer: qx.StreamConsumer, stream_producer: qx.StreamProducer):
        self.stream_consumer = stream_consumer
        self.stream_producer = stream_producer

        self.parameter_name = os.environ["ParameterName"]
        self.percentage_points_alert = float(os.environ["PercentagePointsAlert"])
        self.global_max = None
        self.global_max_ti = None
        self.global_min = None
        self.global_min_ti = None

    # Callback triggered for each new parameter data.
    def on_data_frame_handler(self, __: qx.StreamConsumer, df: pd.DataFrame):

        if self.parameter_name not in df.columns:
            return

        if self.global_max is None:
            self._update_global_max_and_min(df_i=df[["timestamp", self.parameter_name]], is_alert=False)
            return

        is_globals_updated = False
        print("Last signal: ", df[self.parameter_name].iloc[-1], " | Current minima: ", self.global_min,
              " | Current maxima: ", self.global_max)

        # Alert if change is bigger than percentage_points_alert: INCREASE
        signal_max = df[self.parameter_name].max()
        t_signal_max = df.loc[df[self.parameter_name] == signal_max, "timestamp"].iloc[0]
        if abs((signal_max - self.global_min) / self.global_min) > self.percentage_points_alert / 100:
            # Generate alert data parameters and update min and max variables
            df['Alert'] = "None"
            df.loc[df["timestamp"] == t_signal_max, 'Alert'] = str(self.percentage_points_alert) + "% increase"
            df[self.parameter_name + '_previous_low_value'] = self.global_min
            df[self.parameter_name + '_previous_low_value_time'] = self.global_min_ti
            self._update_global_max_and_min(df_i=df[["timestamp", self.parameter_name]], is_alert=True)
            is_globals_updated = True
            df.loc[df["timestamp"] > t_signal_max, self.parameter_name + '_previous_low_value'] = self.global_min
            df.loc[
                df["timestamp"] > t_signal_max, self.parameter_name + '_previous_low_value_time'] = self.global_min_ti

            # Output alert data
            cols = ['timestamp', self.parameter_name, 'Alert',
                    self.parameter_name + '_previous_low_value', self.parameter_name + '_previous_low_value_time']
            df_i = df.loc[df["timestamp"] == t_signal_max, cols]
            print("ALERT!")
            print(df_i)
            self.stream_producer.timeseries.buffer.publish(df_i)  # Send alert data to output topic

        # Alert if change is bigger than percentage_points_alert: DECREASE
        signal_min = df[self.parameter_name].min()
        t_signal_min = df.loc[df[self.parameter_name] == signal_min, "timestamp"].iloc[0]
        if abs((self.global_max - signal_min) / signal_min) > self.percentage_points_alert / 100:
            # Generate alert data parameters and update min and max variables
            df['Alert'] = "None"
            df.loc[df["timestamp"] == t_signal_min, 'Alert'] = str(self.percentage_points_alert) + "% decrease"
            df[self.parameter_name + '_previous_high_value'] = self.global_max
            df[self.parameter_name + '_previous_high_value_time'] = self.global_max_ti
            self._update_global_max_and_min(df_i=df[["timestamp", self.parameter_name]], is_alert=True)
            is_globals_updated = True
            df.loc[df["timestamp"] > t_signal_min, self.parameter_name + '_previous_high_value'] = self.global_max
            df.loc[
                df["timestamp"] > t_signal_min, self.parameter_name + '_previous_high_value_time'] = self.global_max_ti

            # Output alert data
            cols = ['timestamp', self.parameter_name, 'Alert',
                    self.parameter_name + '_previous_high_value', self.parameter_name + '_previous_high_value_time']
            df_i = df.loc[df["timestamp"] == t_signal_min, cols]
            print("ALERT!")
            print(df_i)
            self.stream_producer.timeseries.buffer.publish(df_i)  # Send alert data to output topic

        if is_globals_updated == False:
            self._update_global_max_and_min(df_i=df[["timestamp", self.parameter_name]], is_alert=False)

    # Is it the signal value lower or higher than the threshold value?
    def _update_global_max_and_min(self, df_i, is_alert):
        # Calculate max and mins
        signal_max = df_i[self.parameter_name].max()
        t_signal_max = df_i.loc[df_i[self.parameter_name] == signal_max, "timestamp"].iloc[0]
        signal_min = df_i[self.parameter_name].min()
        t_signal_min = df_i.loc[df_i[self.parameter_name] == signal_min, "timestamp"].iloc[0]

        # Update global_max
        if self.global_max is None:
            self.global_max = signal_max
            self.global_max_ti = t_signal_max
        elif signal_max > self.global_max:
            self.global_max = signal_max
            self.global_max_ti = t_signal_max
            if is_alert:
                self.global_min = signal_max
                self.global_min_ti = t_signal_max

                # Update global_min
        if self.global_min is None:
            self.global_min = signal_min
            self.global_min_ti = t_signal_min
        elif signal_min < self.global_min:
            self.global_min = signal_min
            self.global_min_ti = t_signal_min
            if is_alert:
                self.global_max = signal_min
                self.global_max_ti = t_signal_min
