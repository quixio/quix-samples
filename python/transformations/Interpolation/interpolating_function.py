from quixstreaming import StreamReader, StreamWriter, EventData, ParameterData
import pandas as pd
import os


class InterpolatingFunction:
    def __init__(self, input_stream: StreamReader, output_stream: StreamWriter):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.parameters = os.environ["Parameters"]
        self.last_timestamp = None
        self.last_parameters_value = None

    # Callback triggered for each new event.
    def on_event_data_handler(self, data: EventData):
        print(data.value)

        # Here transform your data.
        self.output_stream.events.write(data)

    # Callback triggered for each new parameter data.
    def on_parameter_data_handler(self, data: ParameterData):
        df = data.to_panda_frame()

        # Check if all items exist in the dataframe
        if all(item in df.columns for item in self.parameters) == False:
            return

        # Iterate over dataframe
        for i in range(len(df)):
            df_i = df.iloc[[i], :]
            timestamp_i = df['time'].iloc[i]
            parameters_i = df[self.parameters].iloc[i]

            # If this is the first time we get data in, initiate last_timestamp and last_parameters_value
            if self.last_timestamp is None:
                self.last_timestamp = timestamp_i
                self.last_parameters_value = parameters_i
                continue

            # If it is not the first time we get data, calculate...
            if self.last_timestamp is not None:
                # Time delta in seconds and linear interpolation
                delta_time_seconds = (timestamp_i - self.last_timestamp) / (10 ** 9)
                linear_interpolation_parameters = (parameters_i + self.last_parameters_value) / 2

                # Add new columns to the dataframe
                df_i.loc[:, 'delta_time_seconds'] = delta_time_seconds
                for col in linear_interpolation_parameters.index:
                    df_i['Interpolated_' + str(col)] = linear_interpolation_parameters[col]

                print("Time delta in seconds:", delta_time_seconds)
                print("Interpolation")
                print(linear_interpolation_parameters)
                print()

                # Write data
                self.output_stream.parameters.write(df_i)

                # Update
                self.last_timestamp = timestamp_i
                self.last_parameters_value = parameters_i

