from quixstreams import Application
from quixstreams.sources.base import Source
import paho.mqtt.client as paho
from paho import mqtt
import time
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


class HiveMqSource(Source):
    def __init__(self, mqtt_server, mqtt_port, mqtt_topic):
        super().__init__(name="hivemq-source", shutdown_timeout=10)
        self.mqtt_server = mqtt_server
        self.mqtt_port = int(mqtt_port)
        self.mqtt_topic = mqtt_topic

    def run(self):
        client_id = os.getenv("Quix__Deployment__Id", "default")
        mqtt_client = paho.Client(
            callback_api_version=paho.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            userdata=None,
            protocol=mqtt_protocol_version(),
        )

        # Configure TLS
        mqtt_ca_cert = os.getenv("mqtt_ca_cert")
        if mqtt_ca_cert:
            mqtt_client.tls_set(ca_certs=mqtt_ca_cert, tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        else:
            mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

        mqtt_client.reconnect_delay_set(5, 60)

        # Configure authentication
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

        # MQTT callbacks
        def on_connect(client, userdata, connect_flags, reason_code, properties):
            if reason_code == 0:
                mqtt_client.subscribe(self.mqtt_topic, qos=1)
                print("CONNECTED!")
            else:
                print(f"ERROR! - ({reason_code.value}). {reason_code.getName()}")

        def on_message(client, userdata, msg):
            message_key = str(msg.topic).replace("/", "-")
            print(f"{msg.topic} {msg.qos} {msg.payload}")
            self.produce(key=message_key, value=msg.payload)

        def on_subscribe(client, userdata, mid, reason_code_list, properties):
            print(f"Subscribed: {mid}")
            for reason_code in reason_code_list:
                print(f"\tReason code ({reason_code.value}): {reason_code.getName()}")

        def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
            print(f"DISCONNECTED! Reason code ({reason_code.value}) {reason_code.getName()}!")

        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.on_subscribe = on_subscribe
        mqtt_client.on_disconnect = on_disconnect

        try:
            mqtt_client.connect(self.mqtt_server, self.mqtt_port)
        except Exception as e:
            print(f"ERROR! Failed to connect to MQTT broker at {self.mqtt_server}:{self.mqtt_port}: {e}")
            raise

        mqtt_client.loop_start()

        while self.running:
            time.sleep(1)

        mqtt_client.loop_stop()
        print("Exiting")


def main():
    mqtt_topic = os.getenv("mqtt_topic")
    mqtt_port = os.getenv("mqtt_port", "")
    output_topic_name = os.getenv("output")

    if not output_topic_name:
        print("ERROR! output (topic) environment variable is required")
        raise ValueError("output (topic) environment variable is required")
    if not mqtt_topic:
        print("ERROR! mqtt_topic must be supplied")
        raise ValueError("mqtt_topic must be supplied")
    if not mqtt_port.isnumeric():
        print("ERROR! mqtt_port must be a numeric value")
        raise ValueError("mqtt_port must be a numeric value")

    app = Application()
    output_topic = app.topic(output_topic_name, value_serializer="bytes")
    source = HiveMqSource(
        mqtt_server=os.environ["mqtt_server"],
        mqtt_port=mqtt_port,
        mqtt_topic=mqtt_topic,
    )
    app.add_source(source, output_topic)
    app.run()


if __name__ == "__main__":
    main()
