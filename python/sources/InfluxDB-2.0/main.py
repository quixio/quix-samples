# Import basic utilities
import os
import random
import json
import logging
from time import sleep

# import vendor-specfic modules
from quixstreams import Application
from quixstreams.models.serializers.quix import JSONSerializer, SerializationContext
import influxdb_client

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Quix Application
app = Application.Quix(consumer_group="influxdbv2_sample", auto_create_topics=True)

# Define a serializer for messages, using JSON Serializer for ease
serializer = JSONSerializer()

# Define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

influxdb2_client = influxdb_client.InfluxDBClient(token=os.environ["INFLUXDB_TOKEN"],
                        org=os.environ["INFLUXDB_ORG"],
                        url=os.environ['INFLUXDB_HOST'])

query_api = influxdb2_client.query_api()

measurement = os.environ.get("INFLUXDB_MEASUREMENT_NAME", os.environ["output"])
interval = os.environ.get("task_interval", "5m")
bucket = os.environ.get("INFLUXDB_BUCKET", "placeholder-bucket")

# Global variable to control the main loop's execution
run = True

# Helper function to convert time intervals (like 1h, 2m) into seconds for easier processing.
# This function is useful for determining the frequency of certain operations.
UNIT_SECONDS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
    "y": 31536000,
}

def interval_to_seconds(interval: str) -> int:
    try:
        return int(interval[:-1]) * UNIT_SECONDS[interval[-1]]
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError(
                "interval format is {int}{unit} i.e. '10h'; "
                f"valid units: {list(UNIT_SECONDS.keys())}")
    except KeyError:
        raise ValueError(
            f"Unknown interval unit: {interval[-1]}; "
            f"valid units: {list(UNIT_SECONDS.keys())}")

interval_seconds = interval_to_seconds(interval)

# Function to fetch data from InfluxDB and send it to Quix
# It runs in a continuous loop, periodically fetching data based on the interval.
def get_data():
    # Run in a loop until the main thread is terminated
    while run:
        try:            
            # Query InfluxDB 2.0 using flux
            flux_query = f'''
            from(bucket: "{bucket}")
                |> range(start: -{interval})
                |> filter(fn: (r) => r._measurement == "{measurement}")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
            logger.info(f"Sending query: {flux_query}")

            table = query_api.query_data_frame(query=flux_query,org=os.environ['INFLUXDB_ORG'])

            # Renaming time column to distinguish it from other timestamp types
            table.rename(columns={'_time': 'original_time'}, inplace=True)

            # If there are rows to write to the stream at this time
            if not table.empty:
                json_result = table.to_json(orient='records', date_format='iso')
                yield json_result
                print("query success")
            else:
                print("No new data to publish.")

            # Wait for the next interval
            sleep(interval_seconds)

        except Exception as e:
            print("query failed", flush=True)
            print(f"error: {e}", flush=True)
            sleep(1)

def main():
    """
    Read data from the Query and publish it to Kafka
    """

    # Create a pre-configured Producer object.
    # Producer is already setup to use Quix brokers.
    # It will also ensure that the topics exist before producing to them if
    # Application.Quix is initialized with "auto_create_topics=True".
    producer = app.get_producer()

    with producer:
        for res in get_data():
            # Parse the JSON string into a Python object
            records = json.loads(res)
            for index, obj in enumerate(records):
                # Generate a unique message_key for each row
                message_key = f"INFLUX2_DATA_{str(random.randint(1, 100)).zfill(3)}_{index}"
                logger.info(f"Produced message with key:{message_key}, value:{obj}")

                # Serialize row value to bytes
                serialized_value = serializer(
                    value=obj, ctx=SerializationContext(topic=topic.name)
                )

                # publish the data to the topic
                producer.produce(
                    topic=topic.name,
                    key=message_key,
                    value=serialized_value,
                )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")
