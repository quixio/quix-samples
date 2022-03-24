import paho.mqtt.client as paho
from quixstreaming import StreamReader
from quixstreaming.models.streampackage import StreamPackage


class HiveMQFunction:
    topic_root = 'not_set'

    def __init__(self, topic_root, hivemq_client: paho.Client):
        self.hivemq_client = hivemq_client
        self.topic_root = topic_root

    def package_received_handler(self, s: StreamReader, p: StreamPackage):

        # publish the json data to hivemq
        # topic format is [CHOSEN_TOPIC_ROOT]/[STREAM_ID]/[MESSAGE_TYPE]
        self.hivemq_client.publish(self.topic_root + "/" + s.stream_id + "/" + str(p.type),
                                   payload=p.to_json(), qos=1)
