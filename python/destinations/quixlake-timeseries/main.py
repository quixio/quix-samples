"""
Quix TS Datalake Sink - Main Entry Point

This application consumes data from a Kafka topic and writes it to blob storage as
Hive-partitioned Parquet files with optional Iceberg catalog registration.
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
    auto_offset_reset=os.getenv("AUTO_OFFSET_RESET", "earliest"),
    commit_interval=int(os.getenv("COMMIT_INTERVAL", "30"))
)

# Parse configuration
hive_columns = parse_hive_columns(os.getenv("HIVE_COLUMNS", ""))
table_name = os.getenv("TABLE_NAME") or os.environ["input"]

# Initialize QuixTSDataLakeSink
sink = QuixTSDataLakeSink(
    s3_prefix=os.getenv("S3_PREFIX", "data-lake/time-series"),
    table_name=table_name,
    hive_columns=hive_columns or None,
    timestamp_column=os.getenv("TIMESTAMP_COLUMN", "ts_ms"),
    catalog_url=os.getenv("CATALOG_URL"),
    max_workers=int(os.getenv("MAX_WRITE_WORKERS", "10"))
)

# Create streaming dataframe and attach sink
sdf = app.dataframe(topic=app.topic(os.environ["input"]))
sdf.sink(sink)

logger.info("Starting Quix TS Datalake Sink")
logger.info(f"  Input topic: {os.environ['input']}")
logger.info(f"  Table: {table_name}")
logger.info(f"  Partitioning: {hive_columns if hive_columns else 'none'}")

if __name__ == "__main__":
    app.run()
