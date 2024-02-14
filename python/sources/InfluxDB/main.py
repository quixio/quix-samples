# Importing necessary libraries and modules
from quixstreams import Application
from quixstreams.models.serializers.quix import JSONSerializer, SerializationContext
import os
import random
import influxdb_client_3 as InfluxDBClient3
from time import sleep

# Create an Application
app = Application.Quix(auto_create_topics=True)

# Define a serializer for messages, using JSON Serializer for ease
serializer = JSONSerializer()

# Define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

client = InfluxDBClient3.InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])

measurement_name = os.environ.get("INFLUXDB_MEASUREMENT_NAME", os.environ["output"])
interval = os.environ.get("task_interval", "5m")

# should the main loop run?
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

interval_seconds = interval_to_seconds(interval)

# Function to fetch data from InfluxDB and send it to Quix
# It runs in a continuous loop, periodically fetching data based on the interval.
def get_data():
    # Run in a loop until the main thread is terminated
    while run:
        try:
            # Query InfluxDB 3.0 using influxql or sql
            table = client.query(query=f'SELECT * FROM "{measurement_name}" WHERE time >= now() - {interval}',
                                 language="influxql")

            # Convert the result to a pandas dataframe. Required to be processed through Quix.
            influx_df = table.to_pandas().drop(columns=["iox::measurement"])

            # Convert Timestamp columns to ISO 8601 formatted strings
            datetime_cols = influx_df.select_dtypes(include=['datetime64[ns]']).columns
            for col in datetime_cols:
                influx_df[col] = influx_df[col].dt.isoformat()

            # If there are rows to write to the stream at this time
            if not influx_df.empty:
                yield influx_df
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
    # Iterate over the data from query result
        for df in get_data():
            print(f"DATAFRAME:\n{df}\n")
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
