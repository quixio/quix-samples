import paho.mqtt.client as paho
import quixstreams as qx


class MQTTFunction:
    topic_root = 'not_set'

    def __init__(self, topic_root, mqtt_client: paho.Client):
        self.mqtt_client = mqtt_client
        self.topic_root = topic_root

    def package_received_handler(self, s: qx.StreamConsumer, p: qx.models.streampackage.StreamPackage):

        # publish the json data to mqtt
        # topic format is [CHOSEN_TOPIC_ROOT]/[STREAM_ID]/[MESSAGE_TYPE]
        self.mqtt_client.publish(self.topic_root + "/" + s.stream_id + "/" + str(p.type),
                                   payload = p.to_json(), qos = 1)
