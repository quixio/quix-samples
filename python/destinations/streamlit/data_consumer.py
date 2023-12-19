import os
import quixstreams as qx
import pandas as pd
from data_queue import DataQueue

# Consume data from Quix streams and prepare dataframes for streamlit components.
# Use this class as a template for different data consumers (e.g., per topic/stream)
class DataConsumer():
    def __init__(self, queue: DataQueue) -> None:
        self.queue = queue
        self.data = pd.DataFrame()
        client = qx.QuixStreamingClient()
        self.topic = client.get_topic_consumer(os.environ["input"])
    
    # subscription is moved to start() to give the client of this code more control
    # over when to start receiving data. You can move this logic to constructor if
    # necessary.
    def start(self):
        self.topic.on_stream_received = self._on_stream_recv_handler
        self.topic.subscribe()
    
    def _on_stream_recv_handler(self, sc: qx.StreamConsumer):

        # this function is responsible for doing the heavy lifting for turning
        # raw data into something streamlit can render.
        def on_data_recv_handler(_: qx.StreamConsumer, df: pd.DataFrame):
            df["datetime"] = pd.to_datetime(df["timestamp"])

            # we append data to an existing df and publish the entire df so that
            # when users refresh browsers, they will not lose data.
            if not len(self.data) == 0:
                self.data.loc[len(self.data.index) + 1] = df.iloc[0]
            else:
                for c in df.columns:
                    self.data[c] = df[c]
                    
            # publish a reference to the dataframe. This way all client connections
            # see the same view without copying data unnecessarily.
            self.queue.put(self.data)

        print("New stream: {}".format(sc.stream_id))
        buf = sc.timeseries.create_buffer()
        buf.on_dataframe_released = on_data_recv_handler
