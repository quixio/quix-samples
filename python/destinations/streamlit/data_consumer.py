import os
import quixstreams as qx
import pandas as pd
from data_queue import DataQueue

class DataConsumer():
    def __init__(self, queue: DataQueue) -> None:
        self.queue = queue
        client = qx.QuixStreamingClient()
        self.topic = client.get_topic_consumer(os.environ["input"])
    
    def start(self):
        self.topic.on_stream_received = self._on_stream_recv_handler
        self.topic.subscribe()
    
    def _on_stream_recv_handler(self, sc: qx.StreamConsumer):
        def on_data_recv_handler(_: qx.StreamConsumer, df: pd.DataFrame):
            self.queue.put({"f1_telemetry": df})

        print("New stream: {}".format(sc.stream_id))
        buf = sc.timeseries.create_buffer("Speed", "LapNumber", "EngineTemp")
        buf.on_dataframe_released = on_data_recv_handler
