from quixstreams import Application
import os
import logging
from duck_db_sink import DuckDbSink

# for local dev, you can load env vars from a .env file
from dotenv import load_dotenv
load_dotenv("duckdb-sink/.env")

# Basic logger config
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger("DuckDbSink")


# ───────────────────────────────────────────────
# configuration via env vars
# ───────────────────────────────────────────────
S3_BUCKET = os.environ["S3_BUCKET"]                                   # e.g. "my-data-lake"
S3_PREFIX = os.getenv("S3_PREFIX", os.environ["input"])                          # "events" → s3://bucket/events/
S3_ROOT   = f"s3://{S3_BUCKET}/{S3_PREFIX}/"

TABLE_NAME     = os.getenv("DUCKDB_TABLE", S3_PREFIX)
GUID_PATTERN   = os.getenv("FILENAME_PATTERN", "data_{uuidv4}")
PARTITION_KEYS = os.getenv("PARTITION_BY", "day,hostname").split(",")



logger = logging.getLogger(__name__)


def main():
    """ Here we will set up our Application. """

    # Setup necessary objects
    app = Application(
        consumer_group="duckdb_sink_v1.7",
        auto_create_topics=True,
        auto_offset_reset="latest",
        commit_interval=30,
        commit_every=100000
    )
    my_db_sink = DuckDbSink(
        s3_bucket=S3_BUCKET,
        s3_prefix=S3_PREFIX,
        partition_keys=PARTITION_KEYS,
        guid_pattern=GUID_PATTERN
    )
    
    input_topic = app.topic(name=os.environ["input"])

    sdf = app.dataframe(topic=input_topic)

    sdf.sink(my_db_sink)

    # With our pipeline defined, now run the Application
    app.run()


# It is recommended to execute Applications under a conditional main
if __name__ == "__main__":
    logging.info("Starting...")
    main()