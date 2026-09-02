# import Utility modules
import os

from typing import Optional

# import vendor-specific modules
from quixstreams import Application
from quixstreams.sinks.community.influxdb1 import (
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


def conn_var(new_name: str, legacy_name: str, default: str = None) -> str:
    """
    Read a connection env var by the name the shared influxdb1-config Variable Group injects,
    falling back to the legacy INFLUXDB_* name so deployments created before the rename
    keep working.
    """
    value = os.getenv(new_name) or os.getenv(legacy_name) or default
    if value is None:
        raise KeyError(f"{new_name} (or legacy {legacy_name})")
    return value


# Potential Callables - can manually edit these to instead use your own callables.
# --Required--
measurement_name: MeasurementSetter = os.getenv("INFLUXDB_MEASUREMENT_NAME", "default")
# --Optional--
tag_keys: TagsSetter = _as_iterable("INFLUXDB_TAG_KEYS")
field_keys: FieldsSetter = _as_iterable("INFLUXDB_FIELD_KEYS")
time_setter: Optional[TimeSetter] = col if (col := os.environ.get("TIMESTAMP_COLUMN")) else None


def on_connect_success():
    print("CONNECTED!")


def on_connect_failure(err):
    print(f"ERROR! Failed to connect to InfluxDB: {err}")
    raise err


influxdb_v1_sink = InfluxDB1Sink(
    host=conn_var("INFLUXDB1_HOST", "INFLUXDB_HOST"),
    port=int(conn_var("INFLUXDB1_PORT", "INFLUXDB_PORT")),
    username=conn_var("INFLUXDB1_USERNAME", "INFLUXDB_USERNAME"),
    password=conn_var("INFLUXDB1_PASSWORD", "INFLUXDB_PASSWORD"),
    tags_keys=tag_keys,
    fields_keys=field_keys,
    time_setter=time_setter,
    database=conn_var("INFLUXDB1_DATABASE", "INFLUXDB_DATABASE", "quix"),
    measurement=measurement_name,
    on_client_connect_success=on_connect_success,
    on_client_connect_failure=on_connect_failure,
)


app = Application(
    consumer_group=os.environ.get("CONSUMER_GROUP_NAME", "influxdb-data-writer"),
    auto_offset_reset="earliest",
    commit_every=int(os.environ.get("BUFFER_SIZE", "1000")),
    commit_interval=float(os.environ.get("BUFFER_TIMEOUT", "1")),
)
input_topic = app.topic(os.environ["input"])

sdf = app.dataframe(input_topic)
sdf.sink(influxdb_v1_sink)


if __name__ == "__main__":
    app.run()
