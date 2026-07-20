# import utility modules
import os
import logging
from datetime import datetime, timezone

# import vendor-specific libraries
from quixstreams import Application
from quixstreams.sources.community.influxdb3 import InfluxDB3Source

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Quix Application
app = Application()

# Define the output topic using the "output" environment variable
output_topic = app.topic(os.environ["output"])


def timestamp_setter(record: dict) -> int | None:
    """
    Use the InfluxDB point time as the Kafka message timestamp.

    InfluxQL returns the point time in a "time" column, which arrives here as an
    ISO-8601 string (the source serialises the dataframe with date_format="iso").
    Lifting it onto the Kafka timestamp preserves the original event time rather
    than defaulting to the produce time — this mirrors the "_time" handling in the
    InfluxDB v2 source. The raw value is still kept in the message payload.

    Returns epoch milliseconds, or None to fall back to the Kafka default
    (produce time) when the column is missing or cannot be parsed.
    """
    raw_time = record.get("time")
    if not raw_time:
        return None
    try:
        # Python's fromisoformat handles the trailing "Z" from 3.11 onwards.
        dt = datetime.fromisoformat(str(raw_time).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp() * 1000)
    except ValueError:
        logger.warning(f"Could not parse point time '{raw_time}'; using Kafka default timestamp")
        return None


# InfluxDB3Source uses the modern QuixStreams source API: it queries InfluxDB in
# tumbling "time_delta"-sized windows and produces each row to the topic for you.
#
# Connection config comes from the shared "influxdb3-config" variable group, which
# injects INFLUXDB3_* env vars. Assign the same group to this deployment as to the
# InfluxDB v3 server so host, token, database and org all match automatically.
#
# Note on the host scheme: an "https://" (or bare) host queries over TLS gRPC,
# while an "http://" host uses plaintext gRPC — useful for an internal, non-TLS
# InfluxDB 3 instance.
#
# With no start_date/end_date set, the source tails forward from "now" in
# time_delta windows, so it only sees data written with current timestamps.
source = InfluxDB3Source(
    host=os.environ["INFLUXDB3_HOST"],
    # The token always has a value (from the shared group). A no-auth server
    # ignores it; an auth-enabled server matches it against its admin token.
    token=os.environ["INFLUXDB3_TOKEN"],
    organization_id=os.environ.get("INFLUXDB3_ORG", ""),
    database=os.environ["INFLUXDB3_DATABASE"],
    measurements=os.environ.get("INFLUXDB_MEASUREMENT_NAME"),
    timestamp_setter=timestamp_setter,
    time_delta=os.environ.get("task_interval", "5m"),
)

app.add_source(source, topic=output_topic)

if __name__ == "__main__":
    app.run()
