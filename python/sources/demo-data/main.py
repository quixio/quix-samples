# This code will publish the CSV data to a stream as if the data were being generated in real-time.

import quixstreams as qx
import pandas as pd
import time
from datetime import datetime
import os
import threading

# True = keep original timings
# False = No delay, speed through it as fast as possible
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

#####################
# Create a new stream
#####################
# A stream is a collection of data that belong to a single session of a single source.
# `.create_stream()` will create a stream with a random unique ID.
stream_producer = producer_topic.create_stream()

# To append data into the same stream at a later time, assign a stream id manually.
# stream = producer_topic.create_stream("my-own-stream-id")

# Configure the buffer to publish data as desired.
# In this case every 100 rows.
# See docs for more options. Search "using-a-buffer"
stream_producer.timeseries.buffer.time_span_in_milliseconds = 100


###########################################
# Add / Edit stream properties and metadata
###########################################
stream_producer.properties.name = "F1 Demo Data"  # Give the stream a human-readable name (for the data catalogue).
stream_producer.properties.location = "/demo data"  # Save stream in specific folder to organize your workspace.

# If required, add stream metadata to add context to the time series data.
stream_producer.properties.metadata["version"] = "Version 1"

#####################################################################################
# Define Parameter and Event definitions to describe the data to downstream processes
#####################################################################################
# Motion / world position
stream_producer.timeseries.add_location("Player/Motion/World") \
    .add_definition("Motion_WorldPositionX", "WorldPositionX").set_range(-1000, 1000) \
    .add_definition("Motion_WorldPositionY", "WorldPositionY").set_range(-1000, 1000) \
    .add_definition("Motion_WorldPositionZ", "WorldPositionZ").set_range(-1000, 1000)

# Player input
stream_producer.timeseries.add_location("Player/Input") \
    .add_definition("Steer").set_range(-1, 1) \
    .add_definition("Throttle").set_range(0, 1) \
    .add_definition("Brake", description = "Amount or brake applied").set_range(0, 1)

# Vehicle parameters
stream_producer.timeseries.add_location("Telemetry/Engine") \
    .add_definition("Speed").set_range(0, 400) \
    .add_definition("Gear").set_range(-1, 8) \
    .add_definition("DRS").set_range(0, 1) \
    .add_definition("EngineTemp").set_range(0, 200) \
    .add_definition("Clutch").set_range(0, 200) \
    .add_definition("EngineRPM").set_range(0, 20000)


def publish_row(row):
    # create a DataFrame using the row
    df_row = pd.DataFrame([row])

    # add a new timestamp column with the current data and time
    df_row['Timestamp'] = datetime.now()

    # publish the data to the Quix stream created earlier
    stream_producer.timeseries.buffer.publish(df_row)


def process_csv_file(csv_file):
    global shutting_down

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

    # Numer of times to repeat the data
    iterations = 10

    # Variables for calculating the % done
    update_pct = 1
    total_rows = len(df) * iterations
    published_rows = 0
    n_percent = float(total_rows / 100) * update_pct

    print(f"Publishing {total_rows} rows. (Expect an update every {update_pct}% ({int(n_percent)} rows).")
    if keep_timing:
        print("note: Delays greater than 1 second will be reduced to 1 second for this demo.")
    else:
        print("note: Timing of the original data is being ignored.")

    # repeat the data to ensure the replay lasts long enough to
    # inspect and play with the data
    for iteration in range(0, iterations):

        # If shutdown has been requested, exit the loop.
        if shutting_down:
            break

        row_count = len(df)

        # Publish events when an event happens e.g. lap count, new top speed etc.
        # in this case we just publish a row_count with the number of rows being published
        # and a 'state' of 'started' to signify the start of publishing data.
        # The `event_id` and value can be anything you want.
        stream_producer.events \
            .add_timestamp(datetime.now()) \
            .add_value("row_count", str(row_count)) \
            .add_value("state", "started") \
            .publish()

        # Iterate over the rows and send them to the API
        for index, row in df.iterrows():

            # If shutdown has been requested, exit the loop.
            if shutting_down:
                break

            # Create a dictionary that includes both column headers and row values
            row_data = {header: row[header] for header in headers}

            # Publish the data
            publish_row(row_data)

            # Increment the number of published rows
            published_rows += 1
            if int(published_rows % n_percent) == 0:
                print(f"{int(100 * float(published_rows) / float(total_rows))}% published")

            # Delay sending the next row if it exists
            # The delay is calculated using the original timestamps and ensure the data 
            # is published at a rate similar to the original data rates
            if keep_timing and index + 1 < len(df):
                current_timestamp = pd.to_datetime(row['original_timestamp'])
                next_timestamp = pd.to_datetime(df.at[index + 1, 'original_timestamp'])
                time_difference = next_timestamp - current_timestamp
                delay_seconds = time_difference.total_seconds()

                # Cater for negative sleep values
                if delay_seconds < 0:
                    delay_seconds = 0
                    
                # For this demo, if the delay is greater than 1 second, just delay for 1 second
                if delay_seconds > 1:
                    # Uncomment this line if you want to know when a delay is shortened
                    # print(f"Skipping long delay of {delay_seconds} between timestamps.")
                    delay_seconds = 1

                time.sleep(delay_seconds)

        # Publish events when an event happens e.g. lap count, new top speed etc.
        # in this case we just publish a 'state' of 'finished' to signify the end
        # of publishing data. The `event_id` and value can be anything you want.
        stream_producer.events \
            .add_timestamp(datetime.now()) \
            .add_value("state", "finished") \
            .publish()

    print("All rows published.")

    # Close the stream when publishing has ended
    # The stream can be reopened an ay time.
    print("Closing the stream.")
    stream_producer.close()


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
