from quixstreaming import StreamWriter
import paho.mqtt.client as paho
from datetime import datetime


class HiveMQFunction:

    def __init__(self, topic, hivemq_client: paho.Client, output_stream: StreamWriter):
        self.hivemq_client = hivemq_client
        self.topic = topic
        self.output_stream = output_stream

    def handle_hivemq_connected(self):

        # publish an event when we connect
        self.output_stream.events \
            .add_timestamp(datetime.utcnow()) \
            .add_value("CONNECT", "Connected to HiveMQ") \
            .write()

        # once connection is confirmed, subscribe to the topic
        self.hivemq_client.subscribe(self.topic, qos=1)

    def handle_hivemq_message(self, topic, payload, qos):

        # publish message data to a new event
        # if you want to handle the message in a different way
        # implement your own logic here.
        self.output_stream.events \
            .add_timestamp(datetime.utcnow()) \
            .add_value(topic, str(payload)) \
            .add_tag("qos", str(qos)) \
            .write()