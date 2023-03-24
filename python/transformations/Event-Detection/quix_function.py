import quixstreams as qx
import pandas as pd


class QuixFunction:
    def __init__(self, consumer_stream: qx.StreamConsumer, producer_stream: qx.StreamProducer):
        self.consumer_stream = consumer_stream
        self.producer_stream = producer_stream

    # Callback triggered for each new event
    def on_event_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.EventData):
        print(data.value)

        # Transform your data here.

        self.producer_stream.events.publish(data)

    # Callback triggered for each new timeseries data
    def on_dataframe_handler(self, stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
        
        output_df = pd.DataFrame()
        output_df["timestamp"] = df["timestamp"]

        if "TAG__LapNumber" in df.columns:
            output_df["TAG__LapNumber"] = df["TAG__LapNumber"]
            
        print(df)

        # If braking force applied is more than 50%, we send True.
        # update this code to apply your own logic or ML model processing
        if "Brake" in df.columns:
            output_df["HardBraking"] = df.apply(lambda row: "True" if row.Brake > 0.5 else "False", axis=1)  

        self.producer_stream.timeseries.buffer.publish(output_df)

