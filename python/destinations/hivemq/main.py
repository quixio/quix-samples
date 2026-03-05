from quixstreams import Application
import paho.mqtt.client as paho
from paho import mqtt
import json
import os

# Load environment variables (useful when working locally)
from dotenv import load_dotenv
load_dotenv()

MQTT_VERSIONS = {
    "3.1": paho.MQTTv31,
    "3.1.1": paho.MQTTv311,
    "5": paho.MQTTv5,
}


def mqtt_protocol_version():
    version = os.environ.get("mqtt_version", "3.1.1")
    protocol = MQTT_VERSIONS.get(version)
    if protocol is None:
        print(f"Unknown MQTT version '{version}', defaulting to 3.1.1")
        return paho.MQTTv311
    print(f"Using MQTT version {version}")
    return protocol


def configure_authentication(mqtt_client):
    mqtt_username = os.getenv("mqtt_username")
    if mqtt_username:
        mqtt_password = os.getenv("mqtt_password")
        if not mqtt_password:
            print("ERROR! mqtt_password must be set when mqtt_username is set")
            raise ValueError("mqtt_password must be set when mqtt_username is set")
        print("Using username & password authentication")
        mqtt_client.username_pw_set(mqtt_username, mqtt_password)
    else:
        print("Using anonymous authentication")


def main():
    mqtt_port = os.environ["mqtt_port"]
    mqtt_tls_enabled = os.getenv("mqtt_tls_enabled", "true").lower() == "true"

    if not mqtt_port.isnumeric():
        print("ERROR! mqtt_port must be a numeric value")
        raise ValueError("mqtt_port must be a numeric value")

    client_id = os.getenv("Quix__Deployment__Id", "default")
    mqtt_client = paho.Client(
        callback_api_version=paho.CallbackAPIVersion.VERSION2,
        client_id=client_id,
        userdata=None,
        protocol=mqtt_protocol_version(),
    )

    if mqtt_tls_enabled:
        print("TLS enabled")
        mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    else:
        print("TLS disabled")

    mqtt_client.reconnect_delay_set(5, 60)
    configure_authentication(mqtt_client)

    # Create a Quix Application
    consumer_group = os.getenv("consumer_group_name", "mqtt_consumer_group")
    app = Application(consumer_group=consumer_group, auto_offset_reset="earliest")
    input_topic = app.topic(os.environ["input"])

    mqtt_topic_root = os.environ["mqtt_topic_root"]

    # MQTT callbacks
    def on_connect(client, userdata, connect_flags, reason_code, properties):
        if reason_code == 0:
            print("CONNECTED!")
        else:
            print(f"ERROR! - ({reason_code.value}). {reason_code.getName()}")

    def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
        print(f"DISCONNECTED! Reason code ({reason_code.value}) {reason_code.getName()}!")

    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect

    try:
        mqtt_client.connect(os.environ["mqtt_server"], int(mqtt_port))
    except Exception as e:
        print(f"ERROR! Failed to connect to MQTT broker at {os.environ['mqtt_server']}:{mqtt_port}: {e}")
        raise

    print("Listening to streams. Press CTRL-C to exit.")

    sdf = app.dataframe(input_topic)

    def publish_to_mqtt(data, key, timestamp, headers):
        message_key_string = key.decode("utf-8")
        json_data = json.dumps(data)
        mqtt_client.publish(
            f"{mqtt_topic_root}/{message_key_string}",
            payload=json_data,
            qos=1,
            retain=True,
        )
        return data

    sdf = sdf.apply(publish_to_mqtt, metadata=True)

    mqtt_client.loop_start()

    print("Starting application")
    app.run()

    mqtt_client.loop_stop()
    print("Exiting")


if __name__ == "__main__":
    main()
