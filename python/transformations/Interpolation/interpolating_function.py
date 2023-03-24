import quixstreams as qx
import pandas as pd
import os


class InterpolatingFunction:
    def __init__(self, stream_consumer: qx.StreamConsumer, stream_producer: qx.StreamProducer):
        self.stream_consumer = stream_consumer
        self.stream_producer = stream_producer
        self.parameters = os.environ["Parameters"].split(",")
        self.last_timestamp = None
        self.last_parameters_value = None

    # Callback triggered for each new event.
    def on_event_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.EventData):
        print(data.value)

        # Here transform your data.
        self.stream_producer.events.write(data)

    # Callback triggered for each new parameter data.
    def on_dataframe_handler(self, stream_consumer: qx.StreamConsumer, df: pd.DataFrame):

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
                self.stream_producer.timeseries.publish(df_i)

                # Update
                self.last_timestamp = timestamp_i
                self.last_parameters_value = parameters_i

