from quixstreams import Application
import paho.mqtt.client as paho
from paho import mqtt
from datetime import datetime
import signal
import json
import time
import sys
import os

# Load environment variables (useful when working locally)
from dotenv import load_dotenv
load_dotenv()

def mqtt_protocol_version():
    if os.environ["mqtt_version"] == "3.1":
        return paho.MQTTv31
    if os.environ["mqtt_version"] == "3.1.1":
        return paho.MQTTv311
    if os.environ["mqtt_version"] == "5":
        return paho.MQTTv5
    raise ValueError('mqtt_version is invalid')

mqtt_topic = os.getenv("mqtt_topic", "")
mqtt_port = os.getenv("mqtt_port", "")
mqtt_username = os.getenv("mqtt_username", "")
mqtt_password = os.getenv("mqtt_password", "")
output_topic_name = os.getenv("output", "")

# Validate the config
if output_topic_name == "":
    raise ValueError("output (topic) environment variable is required")
if mqtt_topic == "":
    raise ValueError('mqtt_topic must be supplied')
if not mqtt_port.isnumeric():
    raise ValueError('mqtt_port must be a numeric value')
if mqtt_username == "":
    raise ValueError('mqtt_username must be supplied')
if mqtt_password == "":
    raise ValueError('mqtt_password must be supplied')

client_id = os.getenv("Quix__Deployment__Name", "default")
mqtt_client = paho.Client(client_id = client_id, userdata = None, protocol = mqtt_protocol_version())
mqtt_client.tls_set(tls_version = mqtt.client.ssl.PROTOCOL_TLS)  # we'll be using tls
mqtt_client.username_pw_set(os.environ["mqtt_username"], os.environ["mqtt_password"])

# Create a Quix Application, this manages the connection to the Quix platform
app = Application()
# Create the producer, this is used to write data to the output topic
producer = app.get_producer()
# create a topic object for use later on
output_topic = app.topic(output_topic_name)


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties = None):
    if rc == 0:
        mqtt_client.subscribe(mqtt_topic, qos = 1)
        print("CONNECTED!") # required for Quix to know this has connected
    else:
        print("ERROR: Connection refused ({})".format(rc))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    message_key = str(msg.topic).replace("/", "-")

    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    # build a payload, here we have the data, qos and a timestamp
    payload = {
        "data": msg.payload.decode('utf-8'),
        "qos": str(msg.qos),
        "timestamp": str(datetime.utcnow())
    }
    payload_string = json.dumps(payload)
    # publish to the putput topic
    producer.produce(topic=output_topic.name,
                    key=message_key,
                    value=payload_string)


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties = None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe

# connect to MQTT Cloud on port 8883 (default for MQTT)
mqtt_client.connect(os.environ["mqtt_server"], int(mqtt_port))

# start the background process to handle MQTT messages
mqtt_client.loop_start()


# Define a handler function that will be called when SIGTERM is received
def handle_sigterm(signum, frame):
    print("SIGTERM received, exiting gracefully")
    sys.exit(0)

# Register the handler for the SIGTERM signal
signal.signal(signal.SIGTERM, handle_sigterm)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    mqtt_client.loop_stop() # clean up
    print("Interrupted by the user")