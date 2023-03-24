import quixstreams as qx
from snowplow_analytics_sdk import event_transformer as et
import pandas as pd
from datetime import datetime


class QuixFunctions:

    def __init__(self, stream_producer: qx.StreamProducer):
        self.stream_producer = stream_producer

    # Callback triggered for each new record.
    def write_data(self, data) -> None:

        # use the snowplow sdk to transform the incoming data
        tx = et.transform(data)

        # convert to data frame
        df = pd.DataFrame.from_dict(tx)

        # add a time stamp to the row
        df["time"] = datetime.now()

        # publish to the stream
        self.stream_producer.timeseries.buffer.write(df)

        print("Published {}".format(df["event_name"].values[0]))
