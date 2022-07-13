import paho.mqtt.client as paho
from quixstreaming import StreamReader
from quixstreaming.models.streampackage import StreamPackage


class MQTTFunction:
    topic_root = 'not_set'

    def __init__(self, topic_root, mqtt_client: paho.Client):
        self.mqtt_client = mqtt_client
        self.topic_root = topic_root

    def package_received_handler(self, s: StreamReader, p: StreamPackage):

        # publish the json data to mqtt
        # topic format is [CHOSEN_TOPIC_ROOT]/[STREAM_ID]/[MESSAGE_TYPE]
        self.mqtt_client.publish(self.topic_root + "/" + s.stream_id + "/" + str(p.type),
                                   payload=p.to_json(), qos=1)
