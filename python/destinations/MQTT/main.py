from quixstreams import Application
from quixstreams.sinks.community.mqtt import MQTTSink
import os

# Load environment variables (useful when working locally)
# from dotenv import load_dotenv
# load_dotenv()

app = Application(
    consumer_group=os.getenv("consumer_group_name", "mqtt_consumer_group"),
    auto_offset_reset="earliest",
)
input_topic = app.topic(os.environ["input"])

sink = MQTTSink(
    client_id=os.getenv("mqtt_client_id", "quix-mqtt-sink"),
    server=os.environ["mqtt_server"],
    port=int(os.environ["mqtt_port"]),
    topic_root=os.environ["mqtt_topic_root"],
    username=os.getenv("mqtt_username"),
    password=os.getenv("mqtt_password"),
    version=os.environ["mqtt_version"],
    retain=os.getenv("mqtt_retain", "true").lower() == "true",
    tls_enabled=os.getenv("mqtt_tls_enabled", "false").lower() == "true",
)

sdf = app.dataframe(topic=input_topic)
sdf.sink(sink)


if __name__ == "__main__":
    app.run()
