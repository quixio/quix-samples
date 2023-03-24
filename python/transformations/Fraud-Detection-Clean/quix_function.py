import quixstreams as qx
from model_lib import clean_function
import pandas as pd


class QuixFunction:

    def __init__(self, stream_producer: qx.StreamProducer):
        self.stream_producer = stream_producer

    def on_dataframe_handler(self, stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
        # iterate the dataframe rows
        for index, row in df.iterrows():
            # Call clean function
            cleaned_df = clean_function(row)

            print("Writing cleaned data")
            print(cleaned_df)

            # write the data to the stream
            self.stream_producer.timeseries.buffer.write(cleaned_df)
