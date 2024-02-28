# import Utility modules
import os
import ast
import datetime
import logging

# import vendor-specific modules
from quixstreams import Application
from quixstreams.models.serializers.quix import JSONDeserializer
from influxdb_client_3 import InfluxDBClient3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
consumer_group_name = os.environ.get('CONSUMER_GROUP_NAME', "influxdb-data-writer")

# Create a Quix platform-specific application instead
app = Application.Quix(consumer_group=consumer_group_name, auto_create_topics=True, auto_offset_reset='earliest')

input_topic = app.topic(os.environ["input"], value_deserializer=JSONDeserializer())

# Read the environment variable and convert it to a dictionary
tag_keys = ast.literal_eval(os.environ.get('INFLUXDB_TAG_KEYS', "[]"))
field_keys = ast.literal_eval(os.environ.get('INFLUXDB_FIELD_KEYS', "[]"))

# Read the environment variable for the field(s) to get.
# For multiple fields, use a list "['field1','field2']"
                                           
influx3_client = InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])

def send_data_to_influx(message):
    logger.info(f"Processing message: {message}")
    try:
        # Get the measurement name to write data to
        measurement_name = os.environ.get('INFLUXDB_MEASUREMENT_NAME', "measurement1")

        # Initialize the tags and fields dictionaries
        tags = {}
        fields = {}

        # Iterate over the tag_dict and field_dict to populate tags and fields
        for tag_key in tag_keys:
            if tag_key in message:
                tags[tag_key] = message[tag_key]

        for field_key in field_keys:
            if field_key in message:
                fields[field_key] = message[field_key]

        logger.info(f"Using tag keys: {', '.join(tags.keys())}")
        logger.info(f"Using field keys: {', '.join(fields.keys())}")

        # Construct the points dictionary
        points = {
            "measurement": measurement_name,
            "tags": tags,
            "fields": fields,
            "time": message['time']
        }

        influx3_client.write(record=points, write_precision="ms")
        
        logger.info(f"{str(datetime.datetime.utcnow())}: Persisted ponts to influx: {points}")
    except Exception as e:
        logger.info(f"{str(datetime.datetime.utcnow())}: Write failed")
        logger.info(e)

sdf = app.dataframe(input_topic)
sdf = sdf.update(send_data_to_influx)

if __name__ == "__main__":
    logger.info("Starting application")
    app.run(sdf)
