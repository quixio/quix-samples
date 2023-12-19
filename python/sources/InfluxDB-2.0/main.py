# Importing necessary libraries and modules
import quixstreams as qx
import os
from threading import Thread
from influxdb_client import InfluxDBClient
from time import sleep
from datetime import datetime, timedelta
import pandas as pd


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


# Quix provides automatic credential injection for the client.
# However, if needed, the SDK token can be provided manually.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# Initializing the Quix output topic for data streaming
print("Opening output topic")
producer_topic = client.get_topic_producer(os.environ["output"])

# Creating a new data stream for Quix
# A stream represents a collection of data belonging to a single session of a source.
# A stream is a collection of data that belong to a single session of a single source.
stream_producer = producer_topic.create_stream()
# Editing the properties of the stream
# Assigning a stream ID allows for appending data to the stream later on.
# stream = producer_topic.create_stream("my-own-stream-id")  # To append data into the stream later, assign a stream id.
stream_producer.properties.name = "influxdb-query"  # Give the stream a human readable name (for the data catalogue).
stream_producer.properties.location = "/influxdb"  # Save stream in specific folder to organize your workspace.
stream_producer.properties.metadata["version"] = "Version 1"  # Add stream metadata to add context to time series data.

client = InfluxDBClient(token=os.environ["INFLUXDB_TOKEN"],
                        url=os.environ["INFLUXDB_HOST"],
                        org=os.environ["INFLUXDB_ORG"])
query_api = client.query_api()

measurement_name = os.environ.get("INFLUXDB_MEASUREMENT_NAME")
interval = os.environ.get("task_interval", "5m")
interval_seconds = interval_to_seconds(interval)

bucket = os.environ["INFLUXDB_BUCKET"]
org = os.environ["INFLUXDB_ORG"]


# Function to fetch data from InfluxDB and send it to Quix
# It runs in a continuous loop, periodically fetching data based on the interval.
def get_data():
    # Run in a loop until the main thread is terminated
    while True:
        start = datetime.now().timestamp()
        flux_query = f'''
            from(bucket: "{bucket}")
                |> range(start: -{interval})
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
        df = query_api.query_data_frame(org=org, query=flux_query)

        # If the query returns tables with different schemas, the result will be a list of dataframes.
        if isinstance(df, list):
            for item in df:
                item["timestamp"] = pd.to_datetime(item["_time"])
                stream_producer.timeseries.buffer.publish(item)
                print(f"Published 1 row to Quix")
        elif isinstance(df, pd.DataFrame) and not df.empty:
            df["timestamp"] = pd.to_datetime(df["_time"])
            stream_producer.timeseries.buffer.publish(df)
            print(f"Published {len(df)} rows to Quix")

        # Wait for the next interval
        wait_time = datetime.now().timestamp() - start + interval_seconds
        if wait_time > 0:
            sleep(wait_time)
        else:
            print(f"Warning: Query took longer than {interval} seconds. Skipping sleep.")


# Main execution check: Ensures the script is being run as a standalone file and not imported as a module.
if __name__ == "__main__":
    print("Getting data from InfluxDB and sending it to Quix. Press CTRL-C to exit.")
    get_data()
