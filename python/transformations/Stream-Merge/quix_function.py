import quixstreams as qx
import pandas as pd
import base64


class QuixFunction:
    def __init__(self, consumer_topic: qx.TopicConsumer, producer_topic: qx.TopicProducer):
        self.consumer_topic = consumer_topic
        self.producer_topic = producer_topic

    # Callback triggered for each new event.
    def on_event_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.EventData):
        print(data.value)

        # Transform your data here.

        self.producer_topic.events.publish(data)

    # Callback triggered for each new parameter data.
    def on_pandas_frame_handler(self, stream_consumer: qx.StreamConsumer, df: pd.DataFrame):

        df["TAG__parent_streamId"] = self.consumer_topic.stream_id
        df['image'] = df["image"].apply(lambda x: str(base64.b64encode(x).decode('utf-8')))

        self.producer_topic.get_or_create_stream("image-feed") \
            .timeseries.buffer.publish(df)
