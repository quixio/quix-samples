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

app = Application.Quix(consumer_group="influx-destination",
                       auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"], value_deserializer=JSONDeserializer())

# Read the environment variable and convert it to a dictionary
tag_dict = ast.literal_eval(os.environ.get('INFLUXDB_TAG_COLUMNS', "{}"))

# Read the environment variable for measurement name
measurement_name = os.environ.get('INFLUXDB_MEASUREMENT_NAME', os.environ["input"])

# Read the environment variable for the field(s) to get.
# For multiple fields, use a list "['field1','field2']"
field_keys = os.environ.get("field_keys", "['field1']")
                                           
influx3_client = InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])

def send_data_to_influx(message):
    logger.info(f"Processing message: {message}")
    try:
        quixtime = message['time']
        # Get the name(s) and value(s) of the selected field(s)
        # Using just a single field in this example for simplicity
        field1_name = field_keys[0]
        field1_value = message[field_keys[0]]

        logger.info(f"Using field keys: {', '.join(field_keys)}")

        # Using point dictionary structure
        # See: https://docs.influxdata.com/influxdb/cloud-dedicated/reference/client-libraries/v3/python/#write-data-using-a-dict
        points = {
            "measurement": measurement_name,
            "tags": tag_dict,
            "fields": {field1_name: field1_value},
            "time": quixtime
        }

        influx3_client.write(record=points, write_precision="ms")
        
        print(f"{str(datetime.datetime.utcnow())}: Persisted measurement to influx.")
    except Exception as e:
        print(f"{str(datetime.datetime.utcnow())}: Write failed")
        print(e)

sdf = app.dataframe(input_topic)
sdf = sdf.update(send_data_to_influx)

if __name__ == "__main__":
    print("Starting application")
    app.run(sdf)
