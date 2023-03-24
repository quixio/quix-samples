import json

import quixstreams as qx


class QuixFunctions:
    topic_root = 'not_set'

    def __init__(self, stream_producer: RawOutputTopic):
        self.stream_producer = stream_producer

    def package_received_handler(self, s: qx.StreamConsumer, p: StreamPackage):

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
        self.stream_producer.write(message)

