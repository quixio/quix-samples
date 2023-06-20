
# This code will publish the CSV data to a stream as if the data were being generated in real-time.

import quixstreams as qx
import pandas as pd
import time
from datetime import datetime
import os


# Quix Platform injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening producer topic.")
# The producer topic is where the data will be published to
# It's the output from this demo data source code.
producer_topic = client.get_topic_producer(os.environ["output"])

# CREATE A NEW STREAM
# A stream is a collection of data that belong to a single session of a single source.
stream_producer = producer_topic.create_stream()

# EDIT STREAM PROPERTIES
# stream = producer_topic.create_stream("my-own-stream-id")  # To append data into the stream later, assign a stream id manually.
stream_producer.properties.name = "F1 Demo Data"  # Give the stream a human readable name (for the data catalogue).
stream_producer.properties.location = "/demo data"  # Save stream in specific folder to organize your workspace.
# stream_producer.properties.metadata["version"] = "Version 1"  # Add stream metadata to add context to time series data.


def publish_row(row):

    # create a DataFrame using the row
    df_row = pd.DataFrame([row])

    # add a new timestamp column with the current data and time
    df_row['Timestamp'] = datetime.now()

    # publish the data to the Quix stream created earlier
    stream_producer.timeseries.publish(df_row)
    

def process_csv_file(csv_file):

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)
    print("File loaded.")

    # Tag columns must have names prefixed with `Tag__`. 
    # These represent data that will not change often, e.g. the lap number and pit status
    # For this data we have several tag values:
    # DriverStatus, LapNumber, LapValidity, PitStatus, Sector, streamId and eventId
    df = df.rename(columns={"DriverStatus": "TAG__DriverStatus"})
    df = df.rename(columns={"LapNumber": "TAG__LapNumber"})
    df = df.rename(columns={"LapValidity": "TAG__LapValidity"})
    df = df.rename(columns={"PitStatus": "TAG__PitStatus"})
    df = df.rename(columns={"Sector": "TAG__Sector"})
    df = df.rename(columns={"streamId": "TAG__streamId"})
    df = df.rename(columns={"eventId": "TAG__eventId"})
    print("TAG columns renamed.")

    # keep the original timestamp to ensure the original timing is maintained
    df = df.rename(columns={"Timestamp": "original_timestamp"})
    print("Timestamp column renamed.")

    # Get the column headers as a list
    headers = df.columns.tolist()

    # repeat the data twice to ensure the replay lasts long enough to 
    # inspect and play with the data
    for _ in range(0, 2):
        row_count = len(df)
        print(f"Publishing {row_count} rows.")

        # Iterate over the rows and send them to the API
        for index, row in df.iterrows():
            # Create a dictionary that includes both column headers and row values
            row_data = {header: row[header] for header in headers}
            publish_row(row_data)

            # Delay sending the next row if it exists
            # The delay is calculated using the original timestamps and ensure the data 
            # is published at a rate similar to the original data rates
            if index + 1 < len(df):
                current_timestamp = pd.to_datetime(row['original_timestamp'])
                next_timestamp = pd.to_datetime(df.at[index + 1, 'original_timestamp'])
                time_difference = next_timestamp - current_timestamp
                delay_seconds = time_difference.total_seconds()
                time.sleep(delay_seconds)

# start processing the CSV
process_csv_file('demo-data.csv')

print("All rows piblished.")
print("Exiting.")

