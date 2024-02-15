# Importing necessary libraries and modules
from quixstreams import Application
from quixstreams.models.serializers.quix import JSONSerializer, SerializationContext
import os
import random
import influxdb_client
from time import sleep
from datetime import datetime
import pandas as pd

# Create an Application
app = Application.Quix(auto_create_topics=True)

# Define a serializer for messages, using JSON Serializer for ease
serializer = JSONSerializer()

# Define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

client = influxdb_client.InfluxDBClient(token=os.environ["INFLUXDB_TOKEN"],
                        org=os.environ["INFLUXDB_ORG"],
                        url=os.environ['INFLUXDB_HOST'])
query_api = client.query_api()

measurement_name = os.environ.get("INFLUXDB_MEASUREMENT_NAME", os.environ["output"])

# Global variable to control the main loop's execution
run = True

# Helper function to convert time intervals (like 1h, 2m) into seconds for easier processing.
# This function is useful for determining the frequency of certain operations.
def interval_to_seconds(interval):
    if not interval:
        raise ValueError("Invalid interval string")

    unit = interval[-1].lower()
    try:
        value = int(interval[:-1])
    except ValueError:
        raise ValueError("Invalid interval format")

    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 3600 * 24
    elif unit == 'mo':
        return value * 3600 * 24 * 30
    elif unit == 'y':
        return value * 3600 * 24 * 365
    else:
        raise ValueError(f"Unknown interval unit: {unit}")


interval = os.environ.get("task_interval", "5m")
interval_seconds = interval_to_seconds(interval)
bucket = os.environ["INFLUXDB_BUCKET"]
measurement = os.environ['INFLUXDB_MEASUREMENT_NAME']

# Function to fetch data from InfluxDB and send it to Quix
# It runs in a continuous loop, periodically fetching data based on the interval.
def get_data():
    # Run in a loop until the main thread is terminated |> range(start: -{interval})
    while True:
        start = datetime.now().timestamp()
        flux_query = f'''
            from(bucket: "{bucket}")
                |> range(start: -{interval})
                |> filter(fn: (r) => r._measurement == "{measurement}")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
        influx_df = query_api.query_data_frame(query=flux_query,org=os.environ['INFLUXDB_ORG'])

        # Convert Timestamp columns to ISO 8601 formatted strings to avoid serialization errors
        datetime_cols = influx_df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
        for col in datetime_cols:
            influx_df[col] = influx_df[col].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        # If the query returns tables with different schemas, the result will be a list of dataframes.
        if isinstance(influx_df, list):
            for item in influx_df:
                yield item
                print(f"Published 1 row to Quix")
        elif isinstance(influx_df, pd.DataFrame) and not influx_df.empty:
            yield influx_df
            print(f"Published {len(influx_df)} rows to Quix")

        # Wait for the next interval
        wait_time = datetime.now().timestamp() - start + interval_seconds
        if wait_time > 0:
            sleep(wait_time)
        else:
            print(f"Warning: Query took longer than {interval} seconds. Skipping sleep.")

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
    # Iterate over the data from query result
        for df in get_data():

            # Generate a unique message_key for each row
            for index, row in df.iterrows():
                message_key = f"INFLUX_DATA_{str(random.randint(1, 100)).zfill(3)}_{index}"

                # Convert the row to a dictionary
                row_data = row.to_dict()

                # Serialize row value to bytes
                serialized_value = serializer(
                    value=row_data, ctx=SerializationContext(topic=topic.name)
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
