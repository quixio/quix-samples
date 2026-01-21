from quixstreams import Application
from quixstreams.sinks.community.mqtt import MQTTSink
import os

# Load environment variables (useful when working locally)
# from dotenv import load_dotenv
# load_dotenv()

app = Application(
    consumer_group=os.getenv("CONSUMER_GROUP", "mqtt_consumer_group"),
    auto_offset_reset="earliest"
)
input_topic = app.topic(os.environ["input"])

sink = MQTTSink(
    client_id=os.environ["MQTT_CLIENT_ID"],
    server=os.environ["MQTT_SERVER"],
    port=int(os.environ["MQTT_PORT"]),
    topic_root=os.environ["MQTT_TOPIC_ROOT"],
    username=os.environ["MQTT_USERNAME"],
    password=os.environ["MQTT_PASSWORD"],
    version=os.environ["MQTT_VERSION"],
    retain=os.getenv("MQTT_RETAIN_MESSAGES", "false").lower() == "true",
    tls_enabled=os.environ["MQTT_USE_TLS"].lower() == "true"
)

sdf = app.dataframe(topic=input_topic)
sdf.sink(sink)


if __name__ == '__main__':
    app.run()
