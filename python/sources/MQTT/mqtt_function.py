from quixstreaming import StreamWriter
import paho.mqtt.client as paho
from datetime import datetime


class MQTTFunction:

    def __init__(self, topic, mqtt_client: paho.Client, output_stream: StreamWriter):
        self.mqtt_client = mqtt_client
        self.topic = topic
        self.output_stream = output_stream

    def handle_mqtt_connected(self):

        # publish an event when we connect
        self.output_stream.events \
            .add_timestamp(datetime.utcnow()) \
            .add_value("CONNECT", "Connected to MQTT") \
            .write()

        # once connection is confirmed, subscribe to the topic
        self.mqtt_client.subscribe(self.topic, qos=1)

    def handle_mqtt_message(self, topic, payload, qos):

        # publish message data to a new event
        # if you want to handle the message in a different way
        # implement your own logic here.
        self.output_stream.events \
            .add_timestamp(datetime.utcnow()) \
            .add_value(topic, str(payload)) \
            .add_tag("qos", str(qos)) \
            .write()