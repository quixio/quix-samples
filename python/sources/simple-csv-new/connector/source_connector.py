import csv
import logging
import json
from typing import Optional, Union, Callable, Any, Iterator

from .connector_templates import (
    SourceConsumer,
    SourceProducer,
    SourceConnector,
    setup_logging
)
from quixstreams.logging import LogLevel
from quixstreams.models.messages import KafkaMessage
from quixstreams.models.serializers import SerializerType
from quixstreams.models.types import MessageKey, MessageValue


logger = logging.getLogger(__name__)

__all__ = ("CsvSourceConnector",)


class CsvConsumer(SourceConsumer):
    """
    A thin wrapper around csv.DictReader for lazy row-based reading of a CSV file
    with a header.
    """

    def __init__(
        self,
        path: str,
        key_parser: Optional[Union[str, Callable[[dict], MessageKey]]] = None,
        value_parser: Optional[Callable[[dict], MessageValue]] = json.dumps,
        **csv_reader_kwargs,
    ):
        """
        :param path: file path to a .csv file
        :param key_parser: how a key is generated for a given data row. Options:
            - None; no key will be generated (default)
            - A string, representing a column name; uses that row's column value.
            - A function that handles the row as a dict.
        :param value_parser: A function for generating resulting message value for the
            row. Default: json.dumps
        :param csv_reader_kwargs: kwargs passthrough to csv.DictReader
        """
        self._path = path
        self._key_parser = key_parser
        self._value_parser = value_parser
        self._file = None
        self._reader = None
        self._reader_kwargs = csv_reader_kwargs

    def _as_message(self, data: dict) -> KafkaMessage:
        """Convenience method to create a kafka-formatted message"""
        return KafkaMessage(
            key=self.key_parser(data),
            value=self.value_parser(data),
            headers=None
        )

    def _consume(self) -> Iterator[dict]:
        """Lazy row reading of the CSV to avoid loading it all in memory"""
        for row in self._reader:
            yield row

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        if not self._file:
            self._file = open(self._path, "r")
            self._reader = csv.DictReader(self._file, **self._reader_kwargs)
            logger.info(f"CSV Consumer beginning reading file: {self._path}")

    def stop(self):
        if self._file:
            logger.info(f"CSV Consumer has stopped reading file: {self._path}")
            self._file.close()
            self._file = None
        self._reader = None

    def key_parser(self, data: dict) -> Optional[MessageKey]:
        """
        :param data: CSV row data as a dict

        :return: a MessageKey type or None
        """
        if self._key_parser:
            if isinstance(self._key_parser, str):
                return data[self._key_parser]
            return self._key_parser(data)

    def value_parser(self, data: dict) -> Optional[MessageValue]:
        """
        :param data: CSV row data as a dict

        :return: a MessageValue type or None
        """
        return self._value_parser(data)

    def consume(self) -> Optional[KafkaMessage]:
        """
        Get a CSV row as a producer-ready message

        :return: a KafkaMessage type when row is available, else None
        """
        try:
            return self._as_message(next(self._consume()))
        except StopIteration:
            logger.info("CSV Consumer has reached the end of the file")
            return


class CsvSourceConnector(SourceConnector):
    """
    A final connector class manages the interactions between consumer and producer.

    This is what the user runs, or can even import.

    In the future, might additionally manage threads or queues to handle various
    use cases? IDK, not sure yet.

    In this case, CSV's are obviously simple enough that they aren't gonna do anything
    fancy like that
    """

    def __init__(
        self,
        csv_path: str,
        topic_name: str,
        default_broker_address: Optional[str] = None,
        key_parser: Optional[Union[str, Callable[[dict], Union[str, bytes]]]] = None,
        value_parser: Optional[Callable[[dict], Any]] = json.dumps,
        kafka_key_serializer: SerializerType = "str",
        kafka_value_serializer: SerializerType = "json",
        loglevel: LogLevel = "INFO",
        **csv_reader_kwargs,
    ):
        """
        :param path: file path to a .csv file
        :param topic_name: name of topic
        :param default_broker_address: broker address (if Quix environment not defined)
        :param key_parser: how a key is generated for a given data row. Options:
            - None; no key will be generated (default)
            - A string, representing a column name; uses that row's column value.
            - A function that handles the row as a dict.
        :param value_parser: A function for generating resulting message value for the
            row. Default: json.dumps
        :param kafka_key_serializer: kafka key serializer; Default "string"
        :param kafka_value_serializer: kafka value serializer; Default "json"
        :param csv_reader_kwargs: kwargs passthrough to csv.DictReader
        """
        setup_logging(loglevel=loglevel)

        self._producer: SourceProducer = SourceProducer(
            topic_name,
            default_broker_address,
            kafka_key_serializer,
            kafka_value_serializer
        )
        self._consumer: CsvConsumer = CsvConsumer(
            csv_path, key_parser, value_parser, **csv_reader_kwargs
        )

    def run(
        self,
        consumer: Optional[CsvConsumer] = None,
        producer: Optional[SourceConsumer] = None
    ):
        producer = producer or self._producer
        consumer = consumer or self._consumer
        with consumer, producer:
            while msg := self._consumer.consume():
                self._producer.produce(key=msg.key, value=msg.value)
