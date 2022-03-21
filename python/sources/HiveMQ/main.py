from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from hivemq_function import HiveMQFunction
import paho.mqtt.client as paho
from paho import mqtt
import os


hivemq_port = os.environ["hivemq_port"]
if not hivemq_port.isnumeric():
    raise ValueError('hivemq_port must be a numeric value')

hivemq_client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
# we'll be using tls
hivemq_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
hivemq_client.username_pw_set(os.environ["hivemq_username"], os.environ["hivemq_password"])

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
quix_client = QuixStreamingClient()

print("Opening output topic")
output_topic = quix_client.open_output_topic(os.environ["output"])

# A stream is a collection of data that belong to a single session of a single source.
output_stream = output_topic.create_stream()

output_stream.properties.name = "HiveMQ Data"  # Give the stream a human-readable name (for the data catalogue).
output_stream.properties.location = "/hivemq data"  # Save stream in specific folder to organize your workspace.

hivemq_functions = HiveMQFunction(os.environ["hivemq_topic"], hivemq_client, output_stream)

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

    # handle the message in the 'connected' function
    hivemq_functions.handle_hivemq_connected()

    print("CONNECTED!")  # required for Quix to know this has connected


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    # handle the message in the relevant function
    hivemq_functions.handle_hivemq_message(msg.topic, msg.payload, msg.qos)


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


hivemq_client.on_connect = on_connect
hivemq_client.on_message = on_message
hivemq_client.on_subscribe = on_subscribe

# connect to HiveMQ Cloud on port 8883 (default for MQTT)
hivemq_client.connect(os.environ["hivemq_server"], int(hivemq_port))

# start the background process to handle MQTT messages
hivemq_client.loop_start()

def before_shutdown():
    # stop handling MQTT messages
    hivemq_client.loop_stop()

# Handle graceful exit of the model.
App.run(before_shutdown=before_shutdown)