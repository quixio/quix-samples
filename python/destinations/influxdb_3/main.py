# import Utility modules
import os
import ast
import datetime
import logging

# import vendor-specific modules
from quixstreams import Application
from quixstreams import message_context
from influxdb_client_3 import InfluxDBClient3

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# read the consumer group from config
consumer_group_name = os.environ.get("CONSUMER_GROUP_NAME", "influxdb-data-writer")

# read the timestamp column from config
timestamp_column = os.environ.get("TIMESTAMP_COLUMN", "")

# Create a Quix platform-specific application instead
app = Application.Quix(consumer_group=consumer_group_name, auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])

# Read the environment variable and convert it to a dictionary
tag_keys = ast.literal_eval(os.environ.get("INFLUXDB_TAG_KEYS", "[]"))
field_keys = ast.literal_eval(os.environ.get("INFLUXDB_FIELD_KEYS", "[]"))

# Read the environment variable for the field(s) to get.
# For multiple fields, use a list "["field1","field2"]"
                                           
influx3_client = InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])

# Get the measurement name to write data to
measurement_name = os.environ.get("INFLUXDB_MEASUREMENT_NAME", "measurement1")


def send_data_to_influx(message):
    logger.info(f"Processing message: {message}")

    # use the column specified for timestamps or the message context
    if timestamp_column == '':
        time = (message_context().timestamp).milliseconds * 1000 * 1000
    else:
        time = message[timestamp_column]

    try:
        # Initialize the tags and fields dictionaries
        tags = {}
        fields = {}

        # Iterate over the tag_dict and field_dict to populate tags and fields
        for tag_key in tag_keys:
            if tag_key in message:
                if message[tag_key] is not None:  # skip None values
                    tags[tag_key] = message[tag_key]

        for field_key in field_keys:
            if field_key in message:
                if message[field_key] is not None:  # skip None values
                    fields[field_key] = message[field_key]

        logger.info(f"Using tag keys: {', '.join(tags.keys())}")
        logger.info(f"Using field keys: {', '.join(fields.keys())}")

        # Check if fields dictionary is not empty
        if not fields and not tags:
            logger.info("Fields and Tags are empty: No data to write to InfluxDB.")
            return  # Skip writing to InfluxDB
        
        # Construct the points dictionary
        points = {
            "measurement": measurement_name,
            "tags": tags,
            "fields": fields,
            "time": time
        }
        
        influx3_client.write(record=points, write_precision="ns")
        
        logger.info(f"{str(datetime.datetime.utcnow())}: Persisted ponts to influx: {points}")
    except Exception as e:
        logger.info(f"{str(datetime.datetime.utcnow())}: Write failed")
        logger.info(e)

sdf = app.dataframe(input_topic)
sdf = sdf.update(send_data_to_influx)

if __name__ == "__main__":
    logger.info("Starting application")
    app.run(sdf)