"""
Quix TS Datalake Sink - Main Entry Point

This application consumes data from a Kafka topic and writes it to blob storage as
Hive-partitioned Parquet files with optional Iceberg catalog registration.

Blob storage is configured via the Quix__BlobStorage__Connection__Json environment variable,
which is automatically handled by the quixportal library. The bucket name is extracted
automatically from this configuration.

File paths follow the workspace-aware structure:
    {workspaceId}/data-lake/time-series/{table_name}/...
"""
import json
import os
import re
import time
import logging
from typing import Optional, Callable

from quixstreams import Application
from quixstreams.sinks.core.quix_ts_datalake_sink import QuixTSDataLakeSink

# Configure logging
logging.basicConfig(
    level=os.getenv("LOGLEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constant for time-series data lake path structure
TIMESERIES_PREFIX = "data-lake/time-series"


_TABLE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*$')


def _positive_int(env_var: str, default: str) -> int:
    raw = os.getenv(env_var, default)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"{env_var} must be a positive integer, got '{raw}'")
    if value <= 0:
        raise ValueError(f"{env_var} must be a positive integer, got {value}")
    return value


def parse_hive_columns(columns_str: str) -> list:
    """
    Parse comma-separated list of partition columns.

    Args:
        columns_str: Comma-separated column names (e.g., "year,month,day")

    Returns:
        List of column names, or empty list if input is empty
    """
    if not columns_str or columns_str.strip() == "":
        return []
    return [col.strip() for col in columns_str.split(",") if col.strip()]


# Initialize Quix Streams Application
commit_interval = _positive_int("COMMIT_INTERVAL", "30")
app = Application(
    consumer_group=os.getenv("CONSUMER_GROUP", "s3_direct_sink_v1.0"),
    auto_offset_reset=os.getenv("AUTO_OFFSET_RESET", "latest"),
    commit_interval=commit_interval,
    commit_every=_positive_int("BATCH_SIZE", "1000")
)

# Parse configuration
hive_columns = parse_hive_columns(os.getenv("HIVE_COLUMNS", ""))
auto_discover = os.getenv("AUTO_DISCOVER", "true").lower() == "true"
table_name = os.getenv("TABLE_NAME") or os.environ["input"]
if not _TABLE_NAME_PATTERN.match(table_name):
    raise ValueError(
        f"Invalid table name '{table_name}'. Table names must start with a letter or digit "
        f"and may only contain letters, digits, dots (.), hyphens (-), and underscores (_)."
    )

# Workspace ID (automatically injected by Quix platform)
workspace_id = os.getenv("Quix__Workspace__Id", "")

# ---------------------------------------------------------------------------
# Stream-timeout wiring
#
# A "stream" is one Kafka message key; silence is tracked per key inside
# the sink and the callback is invoked once per silent key. This callback
# runs on the sink thread during flush().
#
# Both env vars have defaults, so the feature is ON by default:
#   STREAM_TIMEOUT_SECONDS = 60
#   STREAM_TIMEOUT_TOPIC   = "timeout-topic"
# Operators disable explicitly by setting STREAM_TIMEOUT_TOPIC="" (empty string);
# unset falls through to the default.
# ---------------------------------------------------------------------------
stream_timeout_topic_name = os.environ.get("STREAM_TIMEOUT_TOPIC", "timeout-topic").strip()
stream_timeout_ms: Optional[int]
on_stream_timeout: Optional[Callable[[str], None]]
side_producer = None

if stream_timeout_topic_name:
    side_producer = app.get_producer()
    _min_timeout_ms = (commit_interval + 1) * 1000
    stream_timeout_ms = _positive_int("STREAM_TIMEOUT_SECONDS", "60") * 1000
    if stream_timeout_ms < _min_timeout_ms:
        logger.warning(
            "STREAM_TIMEOUT_SECONDS too low (%d ms); saturating to commit_interval + 1 s (%d ms)",
            stream_timeout_ms,
            _min_timeout_ms,
        )
        stream_timeout_ms = _min_timeout_ms
    # Register the topic with the Application's topic manager. Under
    # QuixTopicManager this fetches-or-creates the topic via the Quix API
    # and rewrites `.name` to the workspace-prefixed broker name
    # (`<workspace_id>-<name>`), which is what we must pass to the
    # Producer.produce(topic=...) call below. Raw bytes serializers keep
    # the hand-encoded key/value bytes flowing through unchanged.
    stream_timeout_topic = app.topic(
        stream_timeout_topic_name,
        key_serializer="bytes",
        value_serializer="bytes",
    )
    def on_stream_timeout(stream: str) -> None:
        """Timeout handler for one silent Kafka message key.

        The sink passes the decoded message key (a str) once that key has
        been silent past the threshold. Logs INFO and produces one Kafka
        message to STREAM_TIMEOUT_TOPIC with payload:
            value = {"ts_ms": <wall-clock-ms>, "stream": <key>,
                     "event": "stream_timeout"}
        The Kafka record key is the UTF-8 bytes of ``stream``.

        Fire-and-forget: this callback runs on the sink's flush thread
        (which is the Application processing thread). Calling a blocking
        ``side_producer.flush()`` here would stop the consumer from
        polling for up to librdkafka's ``message.timeout.ms`` (~5 min
        default), triggering a rebalance and offset-reset cascade. The
        underlying producer polls in the background, so the message is
        delivered asynchronously; we only need ``produce()``.
        """
        logger.info("Stream %s timed out after inactivity", stream)
        side_producer.produce(
            topic=stream_timeout_topic.name,
            key=stream.encode() if isinstance(stream, str) else stream,
            value=json.dumps({
                "ts_ms": int(time.time() * 1000),
                "stream": stream,
                "event": "stream_timeout",
            }).encode(),
        )
        # DO NOT call side_producer.flush() here — see docstring above.
else:
    stream_timeout_ms = None
    on_stream_timeout = None

logger.info(
    "Stream-timeout tracking: %s",
    f"enabled ({stream_timeout_ms} ms → topic {stream_timeout_topic_name!r})"
    if stream_timeout_ms is not None
    else "disabled",
)

# Initialize QuixLakeSink
# Note: Blob storage credentials are configured via Quix__BlobStorage__Connection__Json
# environment variable, which is automatically read by quixportal.
# The bucket name is extracted automatically from the quixportal configuration.
blob_sink = QuixTSDataLakeSink(
    s3_prefix=TIMESERIES_PREFIX,
    table_name=table_name,
    workspace_id=workspace_id,
    hive_columns=hive_columns,
    timestamp_column=os.getenv("TIMESTAMP_COLUMN", "ts_ms"),
    catalog_url=os.getenv("CATALOG_URL"),
    catalog_auth_token=os.getenv("CATALOG_AUTH_TOKEN", os.getenv("Quix__Sdk__Token", "")),
    auto_discover=auto_discover,
    namespace=os.getenv("CATALOG_NAMESPACE", "default"),
    auto_create_bucket=True,
    max_workers=_positive_int("MAX_WRITE_WORKERS", "10"),
    stream_timeout_ms=stream_timeout_ms,
    on_stream_timeout=on_stream_timeout,
    on_client_connect_success=lambda: print("CONNECTED!"),
    on_client_connect_failure=lambda e: print(f"ERROR! {e}"),
)

# Create streaming dataframe and attach sink
sdf = app.dataframe(topic=app.topic(os.environ["input"]))

# Attach sink (batching is handled by BatchingSink)
sdf.sink(blob_sink)

# Log startup configuration
storage_path = f"{workspace_id}/{TIMESERIES_PREFIX}" if workspace_id else TIMESERIES_PREFIX
logger.info("Starting Quix TS Datalake Sink")
logger.info(f"  Input topic: {os.environ['input']}")
logger.info(f"  Storage path: {storage_path}/{table_name}")
logger.info(f"  Partitioning: {hive_columns if hive_columns else 'none'}")

if __name__ == "__main__":
    if side_producer is not None:
        side_producer.__enter__()
    try:
        app.run()
    finally:
        if side_producer is not None:
            side_producer.__exit__(None, None, None)
