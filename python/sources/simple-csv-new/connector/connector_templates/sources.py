import logging
import os

from abc import ABC, abstractmethod

from quixstreams import Application
from quixstreams.kafka import Producer
from quixstreams.models.messages import KafkaMessage
from quixstreams.models.serializers import SerializerType
from quixstreams.models.topics import Topic
from quixstreams.models.types import MessageKey, MessageValue
from typing import Optional
from typing_extensions import Self

# maybe rename Consumer to "Reader" to not confuse it with a kafka consumer?

logger = logging.getLogger(__name__)

__all__ = ("SourceConsumer", "SourceProducer", "SourceConnector")


class SourceConsumer(ABC):
    """
    Responsible for getting data from a source in a "kafka-friendly" format from
    static or dynamic data sources.
    """

    @abstractmethod
    def consume(self) -> Optional[KafkaMessage]:
        """get a kafka-ready version of the data to produce with"""
        ...

    @abstractmethod
    def key_parser(self, data) -> Optional[MessageKey]:
        """Generate a message key from the raw source data"""
        ...

    @abstractmethod
    def value_parser(self, data) -> Optional[MessageValue]:
        """Generate a message value from the raw source data"""
        ...

    @abstractmethod
    def start(self) -> Self:
        """Initialize any source resources (i.e. a session object, etc.)"""
        ...

    @abstractmethod
    def stop(self):
        """Clean up/close any source resources (i.e. a session object, etc.)"""
        ...

    @abstractmethod
    def __enter__(self) -> Self:
        """Does "start" with context manager"""
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Does "stop" with context manager"""
        ...


class MissingBrokerAddress(Exception):
    pass


class SourceProducer:
    """
    Responsible for producing a kafka-formatted message to a topic

    Generally will just be re-used everywhere, hence no protocol
    """

    def __init__(
        self,
        topic_name: str,
        default_broker_address: Optional[str] = None,
        key_serializer: SerializerType = "string",
        value_serializer: SerializerType = "json",
    ):
        """
        :param topic_name: name of topic
        :param default_broker_address: broker address (if Quix environment not defined)
        :param key_serializer: kafka key serializer; Default "string"
        :param value_serializer: kafka value serializer; Default "json"
        """

        if os.environ.get("Quix__Sdk__Token"):
            self._quix_app = Application.Quix("none")
        elif default_broker_address:
            self._quix_app = Application(default_broker_address, "none")
        else:
            raise MissingBrokerAddress("Missing broker address for producer.")
        self._topic: Topic = self._quix_app.topic(
            topic_name, key_serializer=key_serializer, value_serializer=value_serializer
        )
        self._producer: Optional[Producer] = None

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def produce(
        self,
        key: Optional[MessageKey] = None,
        value: Optional[MessageValue] = None,
    ):
        """
        :param key: message key
        :param value: message value
        """
        logger.debug(f'Producing {key}: {value}')
        self._producer.produce(key=key, value=value, topic=self._topic.name)

    def start(self):
        self._producer = self._quix_app.get_producer()
        self._producer.__enter__()

    def stop(self):
        self._producer.flush()


class SourceConnector(ABC):

    @abstractmethod
    def run(self, consumer: SourceConsumer, producer: SourceProducer):
        ...
