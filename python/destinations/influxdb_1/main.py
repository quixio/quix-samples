# import Utility modules
import os

from typing import Optional

# import vendor-specific modules
from quixstreams import Application
from quixstreams.sinks.core.influxdb1 import (
    InfluxDB1Sink,
    FieldsSetter,
    MeasurementSetter,
    TagsSetter,
    TimeSetter,
)

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()


def _as_iterable(env_var) -> list[str]:
    return keys.split(",") if (keys := os.environ.get(env_var)) else []


# Potential Callables - can manually edit these to instead use your own callables.
# --Required--
measurement_name: MeasurementSetter = os.getenv("INFLUXDB_MEASUREMENT_NAME", "default")
# --Optional--
tag_keys: TagsSetter = _as_iterable("INFLUXDB_TAG_KEYS")
field_keys: FieldsSetter = _as_iterable("INFLUXDB_FIELD_KEYS")
time_setter: Optional[TimeSetter] = col if (col := os.environ.get("TIMESTAMP_COLUMN")) else None


influxdb_v1_sink = InfluxDB1Sink(
    host=os.environ["INFLUXDB_HOST"],
    port=int(os.environ["INFLUXDB_PORT"]),
    username=os.environ["INFLUXDB_USERNAME"],
    password=os.environ["INFLUXDB_PASSWORD"],
    tags_keys=tag_keys,
    fields_keys=field_keys,
    time_setter=time_setter,
    database=os.getenv("INFLUXDB_DATABASE", "quix"),
    measurement=measurement_name,
)


app = Application(
    consumer_group=os.environ.get("CONSUMER_GROUP_NAME", "influxdb-data-writer"),
    auto_offset_reset="earliest",
    commit_every=int(os.environ.get("BUFFER_SIZE", "1000")),
    commit_interval=float(os.environ.get("BUFFER_DELAY", "1")),
)
input_topic = app.topic(os.environ["input"])

sdf = app.dataframe(input_topic)
sdf.sink(influxdb_v1_sink)


if __name__ == "__main__":
    app.run()
