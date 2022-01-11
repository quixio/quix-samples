from quixstreaming import StreamWriter
from datetime import datetime


class TwitterFunction:

    def __init__(self, stream_writer: StreamWriter):
        self.stream_writer = stream_writer

    def data_handler(self, matching_rules, data):

        print("Writing tweet {} to stream".format(data["id"]))

        # write the tweet id, text and rule name to Quix
        self.stream_writer.parameters.buffer.add_timestamp(datetime.utcnow()) \
            .add_tag("tag", matching_rules[0]["tag"]) \
            .add_value("tweet_id", data["id"]) \
            .add_value("text", data["text"]) \
            .write()
