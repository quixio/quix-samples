from quixstreaming import QuixStreamingClient, StreamReader
from hivemq_function import HiveMQFunction
from quixstreaming.app import App
import paho.mqtt.client as paho
from paho import mqtt
import os

hivemq_port = os.environ["hivemq_port"]
if not hivemq_port.isnumeric():
    raise ValueError('hivemq_port must be a numeric value')

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
quix_client = QuixStreamingClient()

print("Opening input topic")
input_topic = quix_client.open_input_topic(os.environ["input"], "default-consumer-group")


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)
    print("CONNECTED!")  # required for Quix to know this has connected


hivemq_client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
hivemq_client.on_connect = on_connect
hivemq_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
hivemq_client.username_pw_set(os.environ["hivemq_username"], os.environ["hivemq_password"])

hivemq_topic_root = os.environ["hivemq_topic_root"]

# connect to HiveMQ Cloud on port 8883 (default for MQTT)
hivemq_client.connect(os.environ["hivemq_server"], hivemq_port)


# Callback called for each incoming stream
def read_stream(input_stream: StreamReader):

    # handle the data in a function to simplify the example
    hivemq_function = HiveMQFunction(hivemq_topic_root, hivemq_client)

    # React to new data received from input topic.
    input_stream.events.on_read += hivemq_function.on_event_data_handler
    input_stream.parameters.on_read += hivemq_function.on_parameter_data_handler


input_topic.on_stream_received += read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# start the background process to handle MQTT messages
hivemq_client.loop_start()

def before_shutdown():
    # stop handling MQTT messages
    hivemq_client.loop_stop()

# Handle graceful exit of the model.
App.run(before_shutdown=before_shutdown)
