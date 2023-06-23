# This code will publish the CSV data to a stream as if the data were being generated in real-time.

import quixstreams as qx
import pandas as pd
import time
from datetime import datetime
import os
import threading

# True = keep original timings.
# False = No delay! Speed through it as fast as possible.
keep_timing = True

# If the process is terminated on the command line or by the container
# setting this flag to True will tell the loops to stop and the code
# to exit gracefully.
shutting_down = False

# Quix Platform injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

print("Opening producer topic.")
# The producer topic is where the data will be published to
# It's the output from this demo data source code.
producer_topic = client.get_topic_producer(os.environ["Topic"])

# CREATE A NEW STREAM
# A stream is a collection of data that belong to a single session of a single source.
stream_producer = producer_topic.create_stream()

# Configure the buffer to publish data as desired.
# In this case every 100 rows.
# See docs for more options. Search "using-a-buffer"
stream_producer.timeseries.buffer.time_span_in_milliseconds = 100

# EDIT STREAM PROPERTIES
# stream = producer_topic.create_stream("my-own-stream-id")  # To append data into the stream later, assign a stream id manually.
stream_producer.properties.name = "Demo Data"  # Give the stream a human readable name (for the data catalogue).
stream_producer.properties.location = "/demo data"  # Save stream in specific folder to organize your workspace.
# stream_producer.properties.metadata["version"] = "Version 1"  # Add stream metadata to add context to time series data.

# counters for the status messages
row_counter = 0
published_total = 0

# how many times you want to loop through the data
iterations = 10

def publish_row(row):
    global row_counter
    global published_total

    # create a DataFrame using the row
    df_row = pd.DataFrame([row])

    # add a new timestamp column with the current data and time
    df_row['Timestamp'] = datetime.now()

    # publish the data to the Quix stream created earlier
    stream_producer.timeseries.publish(df_row)

    row_counter += 1

    if row_counter == 10:
        row_counter = 0
        published_total += 10
        print(f"Published {published_total} rows")
    

def process_csv_file(csv_file):
    global shutting_down
    global iterations

    # Read the CSV file into a pandas DataFrame
    print("CSV file loading.")
    df = pd.read_csv(csv_file)
    print("File loaded.")

    row_count = len(df)
    print(f"Publishing {row_count * iterations} rows.")

    has_timestamp_column = False

    # If the data contains a 'Timestamp'
    if "Timestamp" in df:
        has_timestamp_column = True
        # keep the original timestamp to ensure the original timing is maintained
        df = df.rename(columns={"Timestamp": "original_timestamp"})
        print("Timestamp column renamed.")

    # Get the column headers as a list
    headers = df.columns.tolist()

    # repeat the data 10 times to ensure the replay lasts long enough to 
    # inspect and play with the data
    for _ in range(0, iterations):

         # If shutdown has been requested, exit the loop.
        if shutting_down:
            break
        
        # Iterate over the rows and send them to the API
        for index, row in df.iterrows():

             # If shutdown has been requested, exit the loop.
            if shutting_down:
                break

            # Create a dictionary that includes both column headers and row values
            row_data = {header: row[header] for header in headers}
            publish_row(row_data)

            if not keep_timing or not has_timestamp_column:
                # Don't want to keep the original timing or no timestamp? Thats ok, just sleep for 200ms
                time.sleep(0.2)
            else:
                # Delay sending the next row if it exists
                # The delay is calculated using the original timestamps and ensure the data 
                # is published at a rate similar to the original data rates
                if index + 1 < len(df):
                    current_timestamp = pd.to_datetime(row['original_timestamp'])
                    next_timestamp = pd.to_datetime(df.at[index + 1, 'original_timestamp'])
                    time_difference = next_timestamp - current_timestamp
                    delay_seconds = time_difference.total_seconds()
                    
                    # handle < 0 delays
                    if delay_seconds < 0:
                        delay_seconds = 0

                    time.sleep(delay_seconds)


# Run the CSV processing in a thread
processing_thread = threading.Thread(target=process_csv_file, args=('demo-data.csv',))
processing_thread.start()


# Run this method before shutting down.
# In this case we set a flag to tell the loops to exit gracefully.
def before_shutdown():
    global shutting_down
    print("Shutting down")

    # set the flag to True to stop the loops as soon as possible.
    shutting_down = True


# keep the app running and handle termination signals.
qx.App.run(before_shutdown = before_shutdown)

print("Exiting.")
