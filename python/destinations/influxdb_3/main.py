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
from typing import List, Dict

from influxdb_client_3 import Point, InfluxDBClient3

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# read the consumer group from config
consumer_group_name = os.environ.get("CONSUMER_GROUP_NAME", "influxdb-data-writer")

# read the timestamp column from config
timestamp_column = os.environ.get("TIMESTAMP_COLUMN", "")

# Create a Quix platform-specific application instead
app = Application.Quix(consumer_group=consumer_group_name, auto_offset_reset="earliest", use_changelog_topics=False)

input_topic = app.topic(os.environ["input"], timestamp_extractor=lambda *_: int(time() * 1000))
                                           
influx3_client = InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])

# Get the measurement name to write data to
measurement_name = os.environ.get("INFLUXDB_MEASUREMENT_NAME", "measurement1")

# Initialize a buffer for batching points and a timestamp for the last write
points_buffer = []
service_start_state = True
last_write_time_ns = int(time() * 1e9)  # Convert current time from seconds to nanoseconds


def send_data_to_influx(messages: List[dict]):

    points_buffer = []


    for message in messages:
        if timestamp_column == '':
            message_time_ns = (message_context().timestamp).milliseconds * 1000 * 1000
        else:
            message_time_ns = message[timestamp_column]

        
        # Initialize the tags and fields dictionaries
        tags = {}
        fields = {}

        # Iterate over the tag_dict and field_dict to populate tags and fields
        if "tags" in message:
            for tag_key in message["tags"]:
                tags[tag_key] = message["tags"][tag_key]

            for field_key in message:
                if field_key == "tags" or field_key == timestamp_column:
                    continue
                fields[field_key] = message[field_key]

        # Check if fields dictionary is not empty
        if not fields and not tags:
            logger.debug("Fields and Tags are empty: No data to write to InfluxDB.")
            return  # Skip writing to InfluxDB
        
        # Create a new Point and add it to the buffer
        point = Point(measurement_name).time(message_time_ns)
        for tag_key, tag_value in tags.items():
            point.tag(tag_key, tag_value)
        for field_key, field_value in fields.items():
            point.field(field_key, field_value)
        points_buffer.append(point.to_line_protocol())

    for point in points_buffer:
            logger.debug(f"Line Protocol: {point}")

    with influx3_client as client:
        logger.info(f"Writing batch of {len(points_buffer)} points written to InfluxDB.")
        
        client.write(record=points_buffer)

 

sdf = app.dataframe(input_topic)
sdf = sdf.tumbling_window(1000, 1000).reduce(lambda state, row: state + [row], lambda row: [row]).final()
sdf = sdf.apply(lambda row: row["value"]).update(send_data_to_influx)

if __name__ == "__main__":
    logger.info("Starting application")
    app.run(sdf)