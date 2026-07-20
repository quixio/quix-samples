# import Utility modules
import os

# import vendor-specific modules
from quixstreams import Application
from quixstreams.sinks.core.influxdb3 import InfluxDB3Sink

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()


tag_keys = keys.split(",") if (keys := os.environ.get("INFLUXDB_TAG_KEYS")) else []
field_keys = keys.split(",") if (keys := os.environ.get("INFLUXDB_FIELD_KEYS")) else []
measurement_name = os.environ.get("INFLUXDB_MEASUREMENT_NAME", "measurement1")
time_setter = col if (col := os.environ.get("TIMESTAMP_COLUMN")) else None
# Precision of the TIMESTAMP_COLUMN values (ns, us, ms, s). Defaults to nanoseconds.
time_precision = os.environ.get("INFLUXDB_TIME_PRECISION", "ns")

def on_connect_success():
    print("CONNECTED!")


def on_connect_failure(err):
    print(f"ERROR! Failed to connect to InfluxDB: {err}")
    raise err


# Connection config comes from the shared "influxdb3-config" variable group, which
# injects INFLUXDB3_* env vars. Assign the same group to this deployment as to the
# InfluxDB v3 server so host, token, database and org all match automatically.
influxdb_v3_sink = InfluxDB3Sink(
    # The token always has a value (from the shared group). A no-auth server
    # ignores it; an auth-enabled server matches it against its admin token.
    token=os.environ["INFLUXDB3_TOKEN"],
    host=os.environ["INFLUXDB3_HOST"],
    organization_id=os.environ.get("INFLUXDB3_ORG", ""),
    tags_keys=tag_keys,
    fields_keys=field_keys,
    time_setter=time_setter,
    # time_setter values are interpreted at this precision (default nanoseconds).
    time_precision=time_precision,
    database=os.environ["INFLUXDB3_DATABASE"],
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
sdf.sink(influxdb_v3_sink)


if __name__ == "__main__":
    app.run()
