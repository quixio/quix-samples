import quixstreams as qx
from datetime import datetime


class TwitterFunction:

    def __init__(self, stream_producer: qx.StreamProducer):
        self.stream_producer = stream_producer

    def data_handler(self, matching_rules, data):

        print("Writing tweet {} to stream".format(data["id"]))

        # write the tweet id, text and rule name to Quix
        self.stream_producer.timeseries.buffer.add_timestamp(datetime.utcnow()) \
            .add_tag("tag", matching_rules[0]["tag"]) \
            .add_value("tweet_id", data["id"]) \
            .add_value("text", data["text"]) \
            .publish()
