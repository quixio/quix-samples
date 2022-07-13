from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from mqtt_function import MQTTFunction
import paho.mqtt.client as paho
from paho import mqtt
import os


mqtt_port = os.environ["mqtt_port"]
if not mqtt_port.isnumeric():
    raise ValueError('mqtt_port must be a numeric value')

mqtt_client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
# we'll be using tls
mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
mqtt_client.username_pw_set(os.environ["mqtt_username"], os.environ["mqtt_password"])

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
quix_client = QuixStreamingClient()

print("Opening output topic")
output_topic = quix_client.open_output_topic(os.environ["output"])

# A stream is a collection of data that belong to a single session of a single source.
output_stream = output_topic.create_stream()

output_stream.properties.name = "MQTT Data"  # Give the stream a human-readable name (for the data catalogue).
output_stream.properties.location = "/mqtt data"  # Save stream in specific folder to organize your workspace.

mqtt_functions = MQTTFunction(os.environ["mqtt_topic"], mqtt_client)

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        mqtt_functions.handle_mqtt_connected()
        print("CONNECTED!") # required for Quix to know this has connected
    else:
        print("ERROR: Connection refused ({})".format(rc))

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    # handle the message in the relevant function
    mqtt_functions.handle_mqtt_message(msg.topic, msg.payload, msg.qos)


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_subscribe = on_subscribe

# connect to MQTT Cloud on port 8883 (default for MQTT)
mqtt_client.connect(os.environ["mqtt_server"], int(mqtt_port))

# start the background process to handle MQTT messages
mqtt_client.loop_start()

def before_shutdown():
    # stop handling MQTT messages
    mqtt_client.loop_stop()

# Handle graceful exit of the model.
App.run(before_shutdown=before_shutdown)