from quixstreams import Application
from quixstreams.sources.community.mqtt import MQTTSource
import os

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()


def on_connect_success():
    print("CONNECTED!")


def on_connect_failure(err):
    print(f"ERROR! Failed to connect to MQTT broker: {err}")
    raise err


def main():
    mqtt_topic = os.getenv("mqtt_topic")
    mqtt_port = os.getenv("mqtt_port", "")
    output_topic_name = os.getenv("output")

    if not output_topic_name:
        raise ValueError("output (topic) environment variable is required")
    if not mqtt_topic:
        raise ValueError("mqtt_topic must be supplied")
    if not mqtt_port.isnumeric():
        raise ValueError("mqtt_port must be a numeric value")

    mqtt_username = os.getenv("mqtt_username")
    mqtt_password = os.getenv("mqtt_password")

    app = Application()
    output_topic = app.topic(output_topic_name, value_serializer="bytes")
    source = MQTTSource(
        topic=mqtt_topic,
        client_id=os.getenv("Quix__Deployment__Id", "default"),
        server=os.environ["mqtt_server"],
        port=int(mqtt_port),
        username=mqtt_username,
        password=mqtt_password,
        version=os.getenv("mqtt_version", "3.1.1"),
        tls_enabled=bool(mqtt_username),
        on_client_connect_success=on_connect_success,
        on_client_connect_failure=on_connect_failure,
    )
    app.add_source(source, output_topic)
    app.run()


if __name__ == "__main__":
    main()
