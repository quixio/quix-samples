# import Utility modules
import os
import ast
from datetime import datetime
import logging
import pickle
from time import time

# import vendor-specific modules
from quixstreams import Application, State
from quixstreams import message_context
from quixstreams.sinks.influxdb_v3 import InfluxDBV3Sink

from influxdb_client_3 import Point, InfluxDBClient3

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# read the consumer group from config
consumer_group_name = os.environ.get("CONSUMER_GROUP_NAME", "influxdb-data-writer")

# read the timestamp column from config
timestamp_column = os.environ.get("TIMESTAMP_COLUMN", "")

buffer_size = int(os.environ.get("BUFFER_SIZE", "1000"))

buffer_delay = float(os.environ.get("BUFFER_DELAY", "1"))

# Create a Quix platform-specific application instead
app = Application(
    consumer_group=consumer_group_name, 
    auto_offset_reset="earliest",
    commit_every=buffer_size,
    commit_interval=buffer_delay)
input_topic = app.topic(os.environ["input"])

# Read the environment variable and convert it to a dictionary
tag_keys = ast.literal_eval(os.environ.get("INFLUXDB_TAG_KEYS", "[]"))
field_keys = ast.literal_eval(os.environ.get("INFLUXDB_FIELD_KEYS", "[]"))
measurement_name = os.environ.get("INFLUXDB_MEASUREMENT_NAME", "measurement1")

influxdb_v3_sink = InfluxDBV3Sink(
                            token=os.environ["INFLUXDB_TOKEN"],
                            host=os.environ["INFLUXDB_HOST"],
                            org=os.environ["INFLUXDB_ORG"],
                            tags_keys=tag_keys,
                            fields_keys=field_keys,
                            time_key=timestamp_column,
                            database=os.environ["INFLUXDB_DATABASE"],
                            measurement=measurement_name)

sdf = app.dataframe(input_topic)

sdf.sink(influxdb_v3_sink)

if __name__ == "__main__":
    logger.info("Starting application")
    app.run(sdf)