import quixstreams as qx
import pandas as pd
import os


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

    # Callback triggered for each new event.
    def on_event_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.EventData):
        print(data)

    # Callback triggered for each new parameter data.
    def on_dataframe_handler(self, stream_consumer: qx.StreamConsumer, df: pd.DataFrame):

        # Get fresh data
        ti = pd.Timestamp(df.loc[0, 'time'])
        
        if self.parameter_name not in df.columns:
            return

        signal_value = float(df.loc[0, self.parameter_name])

        # Update global max and min variables
        max_dif_min_max = (self.percentage_points_alert * 1.5) / 100
        self._update_global_max_and_min(signal_value, ti, max_dif_min_max)

        print("Signal: ", signal_value, " | Current minima: ", self.global_min, " | Current maxima: ", self.global_max)

        # Alert if change is bigger than percentage_points_alert: INCREASE
        if abs((signal_value - self.global_min) / self.global_min) > self.percentage_points_alert / 100:
            # Generate alert data parameters
            df['Alert'] = str(self.percentage_points_alert) + "% increase"
            df[self.parameter_name + '_previous_low_value'] = self.global_min
            df[self.parameter_name + '_previous_low_value_time'] = self.global_min_ti
            cols = [
                'time',
                self.parameter_name,
                'Alert',
                self.parameter_name + '_previous_low_value',
                self.parameter_name + '_previous_low_value_time']
            self.stream_producer.timeseries.buffer.publish(df[cols])  # Send alert data to output topic

            # Update global max
            self.global_max = signal_value
            self.global_max_ti = ti
            self.global_min = signal_value
            self.global_min_ti = ti

            print()
            print()
            print()
            print("ALARM")
            print(df[cols].to_string())
            print()
            print()
            print()

        # Alert if change is bigger than percentage_points_alert: DECREASE
        elif abs((self.global_max - signal_value) / signal_value) > self.percentage_points_alert / 100:
            # Generate alert data parameters
            df['Alert'] = str(self.percentage_points_alert) + "% decrease"
            df[self.parameter_name + '_previous_high_value'] = self.global_max
            df[self.parameter_name + '_previous_high_value_time'] = self.global_max_ti
            cols = [
                'time',
                self.parameter_name,
                'Alert',
                self.parameter_name + '_previous_high_value',
                self.parameter_name + '_previous_high_value_time']
            self.stream_producer.timeseries.buffer.publish(df[cols])  # Send alert data to output topic

            # Update global max
            self.global_max = signal_value
            self.global_max_ti = ti
            self.global_min = signal_value
            self.global_min_ti = ti

            print()
            print()
            print()
            print("ALARM")
            print(df[cols].to_string())
            print()
            print()
            print()

    # Is it the signal value lower or higher than the threshold value?
    def _update_global_max_and_min(self, signal_value, ti, max_dif_min_max):
        # Update global_max
        if self.global_max is None:
            self.global_max = signal_value
            self.global_max_ti = ti
        elif signal_value > self.global_max:
            self.global_max = signal_value
            self.global_max_ti = ti
            # If global_max is updated, update global_min too if it's now too far below
            if abs((self.global_max - self.global_min) / self.global_min) > max_dif_min_max:
                self.global_min = self.global_min + max_dif_min_max * (self.global_max - self.global_min)
                self.global_min_ti = ti
                # Update global_min
        if self.global_min is None:
            self.global_min = signal_value
            self.global_min_ti = ti
        elif signal_value < self.global_min:
            self.global_min = signal_value
            self.global_min_ti = ti
            # If global_min is updated, update global_max too if it's too far above
            if abs((self.global_max - self.global_min) / self.global_min) > max_dif_min_max:
                self.global_max = self.global_max - max_dif_min_max * (self.global_max - self.global_min)
                self.global_max_ti = ti
