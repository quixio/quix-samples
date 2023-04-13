import quixstreams as qx
import pandas as pd
import os


class ThresholdAlert:
    # Initiate
    def __init__(self, producer_stream: qx.StreamProducer):
        self.producer_stream = producer_stream
        self.threshold_value = float(os.environ["thresholdValue"])
        self.parameter_name = os.environ["parameterName"]
        self.original_inequality_side = None  # what side of the inequality (lower or higher) is the original value
        self.previous_value = None
        self.previous_timestamp = None

    # Callback triggered for each new parameter data.
    def on_dataframe_handler(self, _: qx.StreamConsumer, df: pd.DataFrame):

        if self.parameter_name not in df.columns:
            print("Parameter {0} not present in data frame.".format(self.parameter_name))
            return

        signal_value = float(df.loc[0, self.parameter_name])

        # First time we get a value of data we need to check at which side of the inequality we start from
        if self.original_inequality_side is None:
            self.original_inequality_side = self._get_inequality_side(signal_value)
            print()
            print("Starting inequality side detected is: ", self.original_inequality_side)
            print()

        # If we already know at which side of the threshold we started from, we check the current side
        else:
            inequality_side = self._get_inequality_side(signal_value)

            # Are we at the same side we started?
            if self.original_inequality_side != inequality_side:
                # If not, we have past the threshold!
                print("ALERT")
                print("Signal value: ", signal_value)
                print("Threshold: ", self.threshold_value)

                # Populate dataframe with parameters that we'll use for the alert
                df['Threshold'] = self.threshold_value
                df['Previous_{}_Timestamp'.format(self.parameter_name)] = self.previous_timestamp
                df['Previous_{}_Value'.format(self.parameter_name)] = self.previous_value
                alert_columns = [
                    self.parameter_name,
                    'Threshold',
                    'Previous_{}_Timestamp'.format(self.parameter_name),
                    'Previous_{}_Value'.format(self.parameter_name)]
                self.producer_stream.timeseries.buffer.publish(df[alert_columns])  # Send ALERT data to output topic

                # Now let's reset the original_inequality_side
                self.original_inequality_side = None

            else:
                # If we are here we haven't surpassed the threshold
                print(signal_value, ", " + inequality_side + " than the threshold's value: ", self.threshold_value)

                # Let's update previous variables to be ready for next read
                self.previous_value = signal_value
                if "time" in df.columns:
                    self.previous_timestamp = df.loc[0, 'time']
                elif "timestamp" in df.columns:
                    self.previous_timestamp = df.loc[0, 'timestamp']
                else:
                    self.previous_timestamp = pd.Timestamp.now()

    # Is it the signal value lower or higher than the threshold value?
    def _get_inequality_side(self, signal_value):
        if signal_value < self.threshold_value:
            return "lower"
        elif signal_value > self.threshold_value:
            return "higher"
        else:
            return None
