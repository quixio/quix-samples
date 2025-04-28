from dateutil import parser
import os
import inspect
from typing import Any

from quixstreams import Application
from quixstreams.sources.community.influxdb3 import InfluxDB3Source

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()


def get_kwargs_defaults() -> dict[str, Any]:
    """
    Gets the default kwargs of MongoDBSink so they can be passed in instances
    where the user did not provide an environment variable.
    """
    params = inspect.signature(InfluxDB3Source.__init__).parameters.values()
    return {
        param.name: param.default for param in params if
        param.default is not inspect.Parameter.empty
    }


def _measurements():
    if measurements := os.getenv("INFLUXDB_QUERY_MEASUREMENTS"):
        return measurements.split(',')


def _key_setter():
    if column := os.getenv("INFLUXDB_RECORD_KEY_COLUMN"):
        return lambda record: record[column]


def _timestamp_setter():
    if column := os.getenv("INFLUXDB_RECORD_TIMESTAMP_COLUMN"):
        return lambda record: record[column]


def _start_date():
    if date := os.getenv("INFLUXDB_QUERY_START_DATE"):
        return parser.parse(date)


def _end_date():
    if date := os.getenv("INFLUXDB_QUERY_END_DATE"):
        return parser.parse(date)


kwargs_defaults = get_kwargs_defaults()
influxdb3_source = InfluxDB3Source(
    host=os.environ["INFLUXDB_HOST"],
    token=os.environ["INFLUXDB_TOKEN"],
    organization_id=os.environ["INFLUXDB_ORG"],
    database=os.environ["INFLUXDB_DATABASE"],
    measurements=_measurements() or kwargs_defaults["measurements"],
    key_setter=_key_setter() or kwargs_defaults["key_setter"],
    timestamp_setter=_timestamp_setter() or kwargs_defaults["timestamp_setter"],
    measurement_column_name=os.getenv("INFLUXDB_RECORD_MEASUREMENT_COLUMN") or kwargs_defaults["measurement_column_name"],
    sql_query=os.getenv("INFLUXDB_QUERY_SQL") or kwargs_defaults["sql_query"],
    start_date=_start_date() or kwargs_defaults["start_date"],
    end_date=_end_date() or kwargs_defaults["end_date"],
    time_delta=os.getenv("INFLUXDB_QUERY_TIME_DELTA") or kwargs_defaults["time_delta"],
    max_retries=int(retries) if (retries := os.getenv("INFLUXDB_QUERY_MAX_RETRIES")) is not None else kwargs_defaults["max_retries"],
    delay=float(delay) if (delay := os.getenv("INFLUXDB_QUERY_DELAY_SECONDS")) is not None else kwargs_defaults["delay"],
)

# Create a Quix platform-specific application instead
app = Application(
    consumer_group=os.environ.get("CONSUMER_GROUP_NAME", "influxdb-data-source"),
    auto_offset_reset="earliest",
    commit_every=int(os.environ.get("BUFFER_SIZE", "1000")),
    commit_interval=float(os.environ.get("BUFFER_DELAY", "1")),
)
sdf = app.add_source(influxdb3_source, topic=app.topic(name=os.environ["output"]))


if __name__ == '__main__':
    app.run()
