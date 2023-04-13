import quixstreams as qx
import paho.mqtt.client as paho
from datetime import datetime


class MQTTFunction:

    def __init__(self, topic, mqtt_client: paho.Client, producer_topic: qx.TopicProducer):
        self.mqtt_client = mqtt_client
        self.topic = topic
        self.producer_topic = producer_topic

    def handle_mqtt_connected(self):
        # once connection is confirmed, subscribe to the topic
        self.mqtt_client.subscribe(self.topic, qos = 1)

    def handle_mqtt_message(self, topic, payload, qos):
        # publish message data to a new event
        # if you want to handle the message in a different way
        # implement your own logic here.
        self.producer_topic.get_or_create_stream(str(topic).replace("/", "-")).events \
            .add_timestamp(datetime.utcnow()) \
            .add_value("data", payload.decode("utf-8")) \
            .add_tag("qos", str(qos)) \
            .publish()