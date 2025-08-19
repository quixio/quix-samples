from quixstreams import Application
import os
import logging
from s3_direct_sink import S3DirectSink

# for local dev, you can load env vars from a .env file
#from dotenv import load_dotenv
#load_dotenv(".env")

# Basic logger config
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger("S3DirectSink")


# ───────────────────────────────────────────────
# configuration via env vars
# ───────────────────────────────────────────────
# S3 Configuration
S3_BUCKET = os.environ["S3_BUCKET"]  # Required
S3_PREFIX = os.getenv("S3_PREFIX", "data")  # Default to 'data'

# Table Configuration
TABLE_NAME = os.getenv("TABLE_NAME", os.environ.get("input", "kafka_data"))

# Partitioning Configuration
HIVE_COLUMNS = os.getenv("HIVE_COLUMNS", "").split(",") if os.getenv("HIVE_COLUMNS") else []
TIMESTAMP_COLUMN = os.getenv("TIMESTAMP_COLUMN", "ts_ms")
TIMESTAMP_FORMAT = os.getenv("TIMESTAMP_FORMAT", "day")  # day, hour, month

# Optional REST Catalog for table registration
CATALOG_URL = os.getenv("CATALOG_URL")  # Optional
AUTO_DISCOVER = os.getenv("AUTO_DISCOVER", "true").lower() == "true"
CATALOG_NAMESPACE = os.getenv("CATALOG_NAMESPACE", "default")

# Kafka Configuration
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
COMMIT_INTERVAL = int(os.getenv("COMMIT_INTERVAL", "30"))


def main():
    """Set up and run the S3 Direct Sink Application."""
    
    logger.info("Starting S3 Direct Sink...")
    logger.info(f"S3 Target: s3://{S3_BUCKET}/{S3_PREFIX}/{TABLE_NAME}")
    logger.info(f"Partitioning: hive_columns={HIVE_COLUMNS}, timestamp_format={TIMESTAMP_FORMAT}")
    
    # Setup Quix Streams Application
    app = Application(
        consumer_group=os.getenv("CONSUMER_GROUP", "s3_direct_sink_v1.0"),
        auto_create_topics=True,
        auto_offset_reset=os.getenv("AUTO_OFFSET_RESET", "latest"),
        commit_interval=COMMIT_INTERVAL,
        commit_every=BATCH_SIZE
    )
    
    # Create S3 Direct Sink
    s3_sink = S3DirectSink(
        s3_bucket=S3_BUCKET,
        s3_prefix=S3_PREFIX,
        table_name=TABLE_NAME,
        hive_columns=HIVE_COLUMNS,
        timestamp_column=TIMESTAMP_COLUMN,
        timestamp_format=TIMESTAMP_FORMAT,
        catalog_url=CATALOG_URL,
        auto_discover=AUTO_DISCOVER,
        namespace=CATALOG_NAMESPACE
    )
    
    # Get input topic
    input_topic_name = os.environ.get("input", "kafka-input")
    input_topic = app.topic(name=input_topic_name)
    
    # Create streaming dataframe and sink to S3
    sdf = app.dataframe(topic=input_topic)
    sdf.sink(s3_sink)
    
    logger.info(f"Consuming from topic: {input_topic_name}")
    logger.info(f"Writing to S3: s3://{S3_BUCKET}/{S3_PREFIX}/{TABLE_NAME}")
    
    if CATALOG_URL and AUTO_DISCOVER:
        logger.info(f"Table will be auto-registered in REST Catalog on first write")
    
    # Run the application
    app.run()


if __name__ == "__main__":
    main()