from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
import pandas as pd

# Global variables
# original_inequalitie_side tell us at wich side of the inequality (lower or higher) is originally the signal vs the threshold
original_inequalitie_side = None
previous_value = None
previous_timestamp = None


class threshold:
    # Initiate
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter, parameter_name: str,
                 threshold_value: float):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.threshold_value = threshold_value
        self.parameter_name = parameter_name

    # Is it the signal value lower or higher than the threshold value?
    def get_inequality_side(signal_value, threshold_value):
        if signal_value < threshold_value:
            return "lower"
        elif signal_value > threshold_value:
            return "higher"
        else:
            return None

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data)

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):
        global original_inequalitie_side, previous_value, previous_timestamp

        # Get fresh data
        df = data.to_panda_frame()
        signal_value = float(df.loc[0, self.parameter_name])

        # First time we get a value of data we need to check at which side of the inequality we start from
        if original_inequalitie_side == None:
            original_inequalitie_side = threshold.get_inequality_side(signal_value, self.threshold_value)
            print()
            print("Starting inequality side detected is: ", original_inequalitie_side)
            print()

        # If we already know at which side of the threshold we started from, we chech the current side
        else:
            inequalitie_side = threshold.get_inequality_side(signal_value, self.threshold_value)

            # Are we at the same side we started?
            if original_inequalitie_side != inequalitie_side:
                # If not, we have past the threshold!
                print("ALERT")
                print("Signal value: ", signal_value)
                print("Threshold: ", self.threshold_value)

                # Populate dataframe with parameters that we'll use for the alert
                df['Threshold'] = self.threshold_value
                df['Previous_{}_Timestamp'.format(self.parameter_name)] = previous_timestamp
                df['Previous_{}_Value'.format(self.parameter_name)] = previous_value
                alert_columns = [
                    self.parameter_name,
                    'Threshold',
                    'Previous_{}_Timestamp'.format(self.parameter_name),
                    'Previous_{}_Value'.format(self.parameter_name)]
                self.output_stream.parameters.buffer.write(df[alert_columns])  # Send ALERT data to output topic

                # Now let's reset the original_inequalitie_side
                original_inequalitie_side = None

            else:
                # If we are here we haven't surpassed the threshold
                print(signal_value, ", " + inequalitie_side + " than the threshold's value: ", self.threshold_value)

                # Let's update previous variables to be ready for next read
                previous_value = signal_value
                if "time" in df.columns:
                    previous_timestamp = df.loc[0, 'time']
                elif "timestamp" in df.columns:
                    previous_timestamp = df.loc[0, 'timestamp']
                else:
                    previous_timestamp = pd.Timestamp.now()