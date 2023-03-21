import quixstreams as qx
from snowplow_analytics_sdk import event_transformer as et
from datetime import datetime
import pandas as pd


class QuixFunction:
    def __init__(self, stream_consumer: qx.StreamConsumer, stream_producer: qx.StreamProducer):
        self.stream_consumer = stream_consumer
        self.stream_producer = stream_producer

    # Callback triggered for each new event.
    def on_event_data_handler(self, stream_consumer: qx.StreamConsumer, data: qx.EventData):

        # use the snowplow sdk to transform the incoming data
        tx = et.transform(data.value)

        # convert to data frame
        df = pd.DataFrame.from_dict(tx)

        # add a time stamp to the row
        df["timestamp"] = datetime.now()

        # publish to the stream
        self.stream_producer.timeseries.buffer.publish(df)

        print("Published {}".format(df["event_name"].values[0]))
