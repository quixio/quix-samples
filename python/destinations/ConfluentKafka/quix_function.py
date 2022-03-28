import json

from quixstreaming import StreamReader
from quixstreaming.models.streampackage import StreamPackage
from quixstreaming.raw import RawOutputTopic, RawMessage


class QuixFunctions:
    topic_root = 'not_set'

    def __init__(self, output_stream: RawOutputTopic):
        self.output_stream = output_stream

    def package_received_handler(self, s: StreamReader, p: StreamPackage):

        # build the payload object
        payload = {
            "StreamId": s.stream_id,
            "MessageType": str(p.type),
            "Value": p.to_json(),
        }
        # serialize to json
        json_payload = json.dumps(payload)
        # convert to a byte array
        json_payload_bytes = bytearray(json_payload, "ansi")
        # create the RawMessage object
        message = RawMessage(json_payload_bytes)
        # publish the json data to Confluent
        self.output_stream.write(message)

