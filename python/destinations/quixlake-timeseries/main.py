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
import os
import logging

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
app = Application(
    consumer_group=os.getenv("CONSUMER_GROUP", "s3_direct_sink_v1.0"),
    auto_offset_reset=os.getenv("AUTO_OFFSET_RESET", "latest"),
    commit_interval=int(os.getenv("COMMIT_INTERVAL", "30"))
)

# Parse configuration
hive_columns = parse_hive_columns(os.getenv("HIVE_COLUMNS", ""))
auto_discover = os.getenv("AUTO_DISCOVER", "true").lower() == "true"
table_name = os.getenv("TABLE_NAME") or os.environ["input"]

# Workspace ID (automatically injected by Quix platform)
workspace_id = os.getenv("Quix__Workspace__Id", "")

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
    max_workers=int(os.getenv("MAX_WRITE_WORKERS", "10"))
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
    app.run()