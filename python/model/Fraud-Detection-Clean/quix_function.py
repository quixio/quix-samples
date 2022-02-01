from quixstreaming import StreamWriter
from model_lib import clean_function
import pandas as pd


class QuixFunction:

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer

    def on_pandas_frame_handler(self, df: pd.DataFrame):
        # iterate the dataframe rows
        for index, row in df.iterrows():
            # Call clean function
            cleaned_df = clean_function(row)

            print("Writing cleaned data")
            print(cleaned_df)

            # write the data to the stream
            self.stream_writer.parameters.buffer.write(cleaned_df)
