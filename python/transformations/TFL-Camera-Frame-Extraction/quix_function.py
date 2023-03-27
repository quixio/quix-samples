import quixstreams as qx
import pandas as pd
import json
import time
import os
import cv2


class QuixFunction:
    def __init__(self, stream_consumer: qx.StreamConsumer, stream_producer: qx.StreamProducer):
        self.stream_consumer = stream_consumer
        self.stream_producer = stream_producer
        self.frame_rate = int(os.environ["frame_rate"])

    # Callback triggered for each new event.
    def on_event_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.EventData):
        
        camera = json.loads(data.value)
        camera_id = camera["id"]
        lon = float(camera["lon"])
        lat = float(camera["lat"])

        camera_video_feed = list(filter(lambda x: x["key"] == "videoUrl", camera["additionalProperties"]))[0]

        print( camera_video_feed["modified"])

        video_stream = cv2.VideoCapture(camera_video_feed["value"])

        count = 0

        success, image = video_stream.read()
        while success:
            frame = cv2.imencode('.jpg', image)
            if len(frame) <= 1:
                print("no data")
                continue
            
            frame_bytes = frame[1]

            success, image = video_stream.read()
            
            success, image = video_stream.read()
            count += 1

            if (count - 1) % self.frame_rate == 0:
                self.stream_producer.timeseries.buffer.add_timestamp_nanoseconds(time.time_ns()) \
                    .add_value("image", frame_bytes) \
                    .add_value("lon", lon) \
                    .add_value("lat", lat) \
                    .publish()
                    
                print("Sent {0} frame {1}".format(camera_id, count))

    # Callback triggered for each new parameter data.
    def on_dataframe_handler(self, stream_consumer: qx.StreamConsumer, df: pd.DataFrame):
        print(df)

        # Here transform your data.

        self.stream_producer.timeseries.publish(df)
