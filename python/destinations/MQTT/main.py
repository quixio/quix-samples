from quixstreaming import QuixStreamingClient, StreamReader
from mqtt_function import MQTTFunction
from quixstreaming.app import App
import paho.mqtt.client as paho
from paho import mqtt
import os

def mqtt_protocol_version():
    if os.environ["mqtt_version"] == "3.1":
        return paho.MQTTv31
    if os.environ["mqtt_version"] == "3.1.1":
        return paho.MQTTv311
    if os.environ["mqtt_version"] == "5":
        return paho.MQTTv5
    raise ValueError('mqtt_version is invalid')

mqtt_port = os.environ["mqtt_port"]
if not mqtt_port.isnumeric():
    raise ValueError('mqtt_port must be a numeric value')

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
quix_client = QuixStreamingClient()

print("Opening input topic")
input_topic = quix_client.open_input_topic(os.environ["input"], "default-consumer-group")


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)
    print("CONNECTED!")  # required for Quix to know this has connected


mqtt_client = paho.Client(client_id="", userdata=None, protocol=mqtt_protocol_version())
mqtt_client.on_connect = on_connect
mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
mqtt_client.username_pw_set(os.environ["mqtt_username"], os.environ["mqtt_password"])

mqtt_topic_root = os.environ["mqtt_topic_root"]

# connect to MQTT Cloud on port 8883 (default for MQTT)
mqtt_client.connect(os.environ["mqtt_server"], int(mqtt_port))

# Callback called for each incoming stream
def read_stream(input_stream: StreamReader):

    # handle the data in a function to simplify the example
    mqtt_function = mqttFunction(mqtt_topic_root, mqtt_client)

    # hookup the package received event handler
    input_stream.on_package_received += mqtt_function.package_received_handler

input_topic.on_stream_received += read_stream


# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# start the background process to handle MQTT messages
mqtt_client.loop_start()

def before_shutdown():
    # stop handling MQTT messages
    mqtt_client.loop_stop()

# Handle graceful exit of the model.
App.run(before_shutdown=before_shutdown)
