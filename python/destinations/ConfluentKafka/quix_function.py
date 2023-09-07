import json

from quixstreams import StreamConsumer
from quixstreams.models.streampackage import StreamPackage
from quixstreams.raw import RawTopicProducer, RawMessage


class QuixFunctions:
    topic_root = 'not_set'

    def __init__(self, output_stream: RawTopicProducer):
        self.output_stream = output_stream

    def package_received_handler(self, s: StreamConsumer, p: StreamPackage):

        # build the payload object
        payload = {
            "StreamId": s.stream_id,
            "MessageType": str(p.type),
            "Value": p.to_json(),
        }
        # serialize to json
        json_payload = json.dumps(payload)
        # convert to a byte array
        json_payload_bytes = bytearray(json_payload, "UTF-8")
        # create the RawMessage object
        message = RawMessage(json_payload_bytes)
        # publish the json data to Confluent
        self.output_stream.publish(message)

