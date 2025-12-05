from quixstreams import Application
from quixstreams.sources.core.kafka import KafkaReplicatorSource
import os

# for local dev, load env vars from a .env file
# from dotenv import load_dotenv
# load_dotenv()

# Required parameters
source_broker_address = os.environ["SOURCE_BROKER_ADDRESS"]
source_topic = os.environ["SOURCE_TOPIC"]
output_topic_name = os.environ["output"]

# Optional parameters
auto_offset_reset = os.getenv("AUTO_OFFSET_RESET", "latest")
consumer_poll_timeout = os.getenv("CONSUMER_POLL_TIMEOUT", None)
shutdown_timeout = float(os.getenv("SHUTDOWN_TIMEOUT", "10"))
value_deserializer = os.getenv("VALUE_DESERIALIZER", "json")
key_deserializer = os.getenv("KEY_DESERIALIZER", "bytes")

# Build consumer_extra_config for SASL/SSL if credentials are provided
consumer_extra_config = {}
sasl_username = os.getenv("SOURCE_KAFKA_SASL_USERNAME", "")
sasl_password = os.getenv("SOURCE_KAFKA_SASL_PASSWORD", "")
sasl_mechanism = os.getenv("SOURCE_KAFKA_SASL_MECHANISM", "SCRAM-SHA-256")
ssl_ca_location = os.getenv("SOURCE_KAFKA_SSL_CA_LOCATION", "")

if sasl_username and sasl_password:
    consumer_extra_config['sasl.mechanism'] = sasl_mechanism
    consumer_extra_config['security.protocol'] = 'SASL_SSL'
    consumer_extra_config['sasl.username'] = sasl_username
    consumer_extra_config['sasl.password'] = sasl_password
    if ssl_ca_location:
        consumer_extra_config['ssl.ca.location'] = ssl_ca_location

# Convert consumer_poll_timeout to float if provided
if consumer_poll_timeout:
    consumer_poll_timeout = float(consumer_poll_timeout)

# Create a Quix Application for the destination (Quix platform)
app = Application(
    consumer_group=os.environ["CONSUMER_GROUP"],
)

# Create the KafkaReplicatorSource
source = KafkaReplicatorSource(
    name="kafka-replicator",
    app_config=app.config,
    topic=source_topic,
    broker_address=source_broker_address,
    auto_offset_reset=auto_offset_reset,
    consumer_extra_config=consumer_extra_config if consumer_extra_config else None,
    consumer_poll_timeout=consumer_poll_timeout,
    shutdown_timeout=shutdown_timeout,
    value_deserializer=value_deserializer,
    key_deserializer=key_deserializer,
)

output_topic = app.topic(output_topic_name)
app.add_source(source=source, topic=output_topic)


if __name__ == "__main__":
    app.run()