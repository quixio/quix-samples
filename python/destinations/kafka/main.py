import os
from typing import Tuple, Type

from pydantic_settings import (
    BaseSettings as PydanticBaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict
)

from quixstreams import Application
from quixstreams.kafka.configuration import ConnectionConfig

from sink import KafkaReplicatorSink


class SinkConnectionConfig(ConnectionConfig):
    """
    A ConnectionConfig subclass that reads configuration from environment variables
    with a SINK_ prefix.

    This allows users to configure the sink's Kafka connection using environment
    variables like SINK_BOOTSTRAP_SERVERS, SINK_SASL_USERNAME, etc.

    Example:
        export SINK_BOOTSTRAP_SERVERS=kafka:9092
        export SINK_SECURITY_PROTOCOL=SASL_SSL
        export SINK_SASL_MECHANISM=PLAIN
        export SINK_SASL_USERNAME=myuser
        export SINK_SASL_PASSWORD=mypass

        # Then create the config
        config = SinkConnectionConfig()
        sink = KafkaSink(broker_address=config, topic_name="output-topic")
    """

    model_config = SettingsConfigDict(
        env_prefix="SINK_",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[PydanticBaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """
        Enable reading values from environment variables with SINK_ prefix.
        """
        return init_settings, env_settings


app = Application(
    consumer_group=os.environ["CONSUMER_GROUP"],
    auto_offset_reset="earliest",
)
input_topic = app.topic(os.environ['input'])
kafka_sink = KafkaReplicatorSink(
    broker_address=SinkConnectionConfig(),
    topic_name=os.environ["SINK_OUTPUT_TOPIC"],
    key_serializer=os.getenv("SINK_KEY_SERIALIZER", "bytes"),
    value_serializer=os.getenv("SINK_VALUE_SERIALIZER", "json"),
    origin_topic=input_topic,
    auto_create_sink_topic=os.getenv("SINK_AUTO_CREATE_TOPIC", "true").lower() == "true",
)
app.dataframe(input_topic).sink(kafka_sink)


if __name__ == '__main__':
    app.run()
