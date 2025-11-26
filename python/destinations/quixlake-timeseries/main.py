"""
Quix TS Datalake Sink - Main Entry Point

This application consumes data from a Kafka topic and writes it to S3 as
Hive-partitioned Parquet files with optional Iceberg catalog registration.
"""
import os
import logging

from quixstreams import Application
from quixlake_sink import QuixLakeSink

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
    auto_offset_reset=os.getenv("AUTO_OFFSET_RESET", "latest"),
    commit_interval=int(os.getenv("COMMIT_INTERVAL", "30"))
)

# Parse configuration
hive_columns = parse_hive_columns(os.getenv("HIVE_COLUMNS", ""))
auto_discover = os.getenv("AUTO_DISCOVER", "true").lower() == "true"
table_name = os.getenv("TABLE_NAME") or os.environ["input"]

# Initialize QuixLakeSink
s3_sink = QuixLakeSink(
    s3_bucket=os.environ["S3_BUCKET"],
    s3_prefix=os.getenv("S3_PREFIX", "data"),
    table_name=table_name,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_region=os.getenv("AWS_REGION", "us-east-1"),
    s3_endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
    hive_columns=hive_columns,
    timestamp_column=os.getenv("TIMESTAMP_COLUMN", "ts_ms"),
    catalog_url=os.getenv("CATALOG_URL"),
    catalog_auth_token=os.getenv("CATALOG_AUTH_TOKEN"),
    auto_discover=auto_discover,
    namespace=os.getenv("CATALOG_NAMESPACE", "default"),
    auto_create_bucket=True,
    max_workers=int(os.getenv("MAX_WRITE_WORKERS", "10"))
)

# Create streaming dataframe and attach sink
sdf = app.dataframe(topic=app.topic(os.environ["input"]))

# Attach sink (batching is handled by BatchingSink)
sdf.sink(s3_sink)

logger.info("Starting Quix TS Datalake Sink")
logger.info(f"  Input topic: {os.environ['input']}")
logger.info(f"  S3 destination: s3://{os.environ['S3_BUCKET']}/{os.getenv('S3_PREFIX', 'data')}/{table_name}")
logger.info(f"  Partitioning: {hive_columns if hive_columns else 'none'}")

if __name__ == "__main__":
    app.run()
