"""
Quix Lakehouse Sink - Main Entry Point

This application consumes data from a Kafka topic and writes it to blob storage as
Hive-partitioned Parquet files with optional Iceberg catalog registration.

Blob storage is configured via the Quix__BlobStorage__Connection__Json environment variable,
which is automatically handled by the quixportal library. The bucket name is extracted
automatically from this configuration.

File paths follow the workspace-aware structure:
    {workspaceId}/data-lake/time-series/{table_name}/...
"""
import os
import re
import logging
from typing import List, Optional

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


def _optional_positive_int(env_var: str) -> Optional[int]:
    """Read an optional positive integer. Unset or blank -> None (SDK default)."""
    raw = (os.getenv(env_var) or "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(f"{env_var} must be a positive integer, got '{raw}'")
    if value <= 0:
        raise ValueError(f"{env_var} must be a positive integer, got {value}")
    return value


def parse_column_list(columns_str: str) -> List[str]:
    """
    Parse a comma-separated list of column names.

    Args:
        columns_str: Comma-separated column names (e.g., "year,month,day").
            A "~" prefix on an entry is preserved verbatim - the sink reads it
            as a virtual-partition marker.

    Returns:
        List of column names, or an empty list if the input is empty.
    """
    if not columns_str or columns_str.strip() == "":
        return []
    return [col.strip() for col in columns_str.split(",") if col.strip()]


# Initialize Quix Streams Application. `broker_address` is read from KAFKA_BOOTSTRAP_SERVERS for
# local-dev convenience; in Quix Cloud it stays None and the Application picks up Quix__Broker__*
# from the platform.
app = Application(
    broker_address=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    consumer_group=os.getenv("CONSUMER_GROUP", "s3_direct_sink_v1.0"),
    auto_offset_reset=os.getenv("AUTO_OFFSET_RESET", "latest"),
    commit_interval=_positive_int("COMMIT_INTERVAL", "30"),
    commit_every=_positive_int("BATCH_SIZE", "1000")
)

# Parse configuration
hive_columns = parse_column_list(os.getenv("HIVE_COLUMNS", ""))
timestamp_column = os.getenv("TIMESTAMP_COLUMN", "ts_ms")
# Empty/unset -> None so the SDK default applies:
#   stats_columns  None -> every numeric/timestamp column
#   sort_column    None -> lakehouse falls back to timestamp_column
#   row_group_rows None -> 1,000,000 rows per Parquet row group
stats_columns = parse_column_list(os.getenv("STATS_COLUMNS", "")) or None
sort_column = os.getenv("SORT_COLUMN", "").strip() or None
row_group_rows = _optional_positive_int("ROW_GROUP_ROWS")
auto_discover = os.getenv("AUTO_DISCOVER", "true").lower() == "true"
table_name = os.getenv("TABLE_NAME") or os.environ["input"]
if not _TABLE_NAME_PATTERN.match(table_name):
    raise ValueError(
        f"Invalid table name '{table_name}'. Table names must start with a letter or digit "
        f"and may only contain letters, digits, dots (.), hyphens (-), and underscores (_)."
    )

# Workspace ID (automatically injected by Quix platform)
workspace_id = os.getenv("Quix__Workspace__Id", "")

# Initialize QuixLakeSink
# Note: Blob storage credentials are configured via Quix__BlobStorage__Connection__Json
# environment variable, which is automatically read by quixportal.
# The bucket name is extracted automatically from the quixportal configuration.
# Quix Portal injects the Catalog URL under both the Quix naming convention
# (`Quix__Lakehouse__Catalog__Url`) and the PyIceberg one (`CATALOG_URL`) when a Lakehouse Catalog
# deployment exists in the workspace; prefer the Quix name, fall back to the PyIceberg one for
# legacy compatibility. The auth token is only injected under the Quix name — it routes via the
# secrets-bag / secretKeyRef path that the platform uses for the Catalog's own credentials.
blob_sink = QuixTSDataLakeSink(
    s3_prefix=TIMESERIES_PREFIX,
    table_name=table_name,
    workspace_id=workspace_id,
    hive_columns=hive_columns,
    timestamp_column=timestamp_column,
    sort_column=sort_column,
    catalog_url=os.getenv("Quix__Lakehouse__Catalog__Url") or os.getenv("CATALOG_URL"),
    catalog_auth_token=os.getenv("Quix__Lakehouse__Catalog__AuthToken"),
    auto_discover=auto_discover,
    namespace=os.getenv("CATALOG_NAMESPACE", "default"),
    auto_create_bucket=True,
    max_workers=_positive_int("MAX_WRITE_WORKERS", "10"),
    stats_columns=stats_columns,
    row_group_rows=row_group_rows,
    on_client_connect_success=lambda: print("CONNECTED!"),
    on_client_connect_failure=lambda e: print(f"ERROR! {e}"),
)

# Create streaming dataframe and attach sink
sdf = app.dataframe(topic=app.topic(os.environ["input"]))

# Attach sink (batching is handled by BatchingSink)
sdf.sink(blob_sink)

# Log startup configuration
storage_path = f"{workspace_id}/{TIMESERIES_PREFIX}" if workspace_id else TIMESERIES_PREFIX
logger.info("Starting Quix Lakehouse Sink")
logger.info(f"  Input topic: {os.environ['input']}")
logger.info(f"  Storage path: {storage_path}/{table_name}")
logger.info(f"  Partitioning: {hive_columns if hive_columns else 'none'}")
logger.info(f"  Stats columns: {stats_columns if stats_columns else 'all numeric/timestamp'}")
logger.info(f"  Sort column: {sort_column or f'{timestamp_column} (fallback)'}")
logger.info(f"  Row group rows: {row_group_rows or 'sink default'}")

if __name__ == "__main__":
    app.run()