from quixstreams import Application, context
import paho.mqtt.client as paho
from paho import mqtt
import json
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

mqtt_port = os.environ["mqtt_port"]
if not mqtt_port.isnumeric():
    raise ValueError('mqtt_port must be a numeric value')


# Create a Quix platform-specific application instead
app = Application.Quix(consumer_group="mqtt_consumer_group", auto_offset_reset='earliest')

# initialize the topic, this will combine the topic name with the environment details to produce a valid topic identifier
input_topic = app.topic(os.environ["input"])

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties = None):
    print("CONNACK received with code %s." % rc)
    print("CONNECTED!")  # required for Quix to know this has connected


mqtt_client = paho.Client(client_id = "", userdata = None, protocol = mqtt_protocol_version())
mqtt_client.on_connect = on_connect
mqtt_client.tls_set(tls_version = mqtt.client.ssl.PROTOCOL_TLS)
mqtt_client.username_pw_set(os.environ["mqtt_username"], os.environ["mqtt_password"])

mqtt_topic_root = os.environ["mqtt_topic_root"]

# connect to MQTT Cloud on port 8883 (default for MQTT)
mqtt_client.connect(os.environ["mqtt_server"], int(mqtt_port))

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

sdf = app.dataframe(input_topic)

def publish_to_mqtt(data):
    json_data = json.dumps(data)
    message_key_bytes = context.message_key()  # This is your byte array
    message_key_string = message_key_bytes.decode('utf-8')  # Convert to string using utf-8 encoding
    # publish to MQTT
    mqtt_client.publish(mqtt_topic_root + "/" + message_key_string, payload = json_data, qos = 1)

sdf = sdf.apply(publish_to_mqtt)

def main():
    # start the background process to handle MQTT messages
    mqtt_client.loop_start()

    print("Starting application")
    # run the data processing pipeline
    app.run(sdf)

    # stop handling MQTT messages
    mqtt_client.loop_stop()


if __name__ == "__main__":
    main()
