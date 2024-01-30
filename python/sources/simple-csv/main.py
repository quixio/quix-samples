# This code will publish the CSV data to a stream as if the data were being generated in real-time.

# Import the supplimentary Quix Streams modules for interacting with Kafka: 
from quixstreams.kafka import Producer
from quixstreams.platforms.quix import QuixKafkaConfigsBuilder, TopicCreationConfigs
from quixstreams.models.serializers.quix import JSONSerializer, QuixSerializer, SerializationContext

# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

from datetime import datetime
import pandas as pd
import threading
import random
import time
import os

# import the dotenv module to load environment variables from a file
from dotenv import load_dotenv
load_dotenv(override=False)

# True = keep original timings.
# False = No delay! Speed through it as fast as possible.
keep_timing = False

# If the process is terminated on the command line or by the container
# setting this flag to True will tell the loops to stop and the code
# to exit gracefully.
shutting_down = False

# counters for the status messages
row_counter = 0
published_total = 0

# configure/create everything needed to publish data with the Producer class

# Load the relevant configurations from environment variables
# In Quix Cloud, These variables are already preconfigured with defaults
# When running locally, you need to define 'Quix__Sdk__Token' as an environment variable
# Defining 'Quix__Workspace__Id' is also preferable, but often the workspace ID can be inferred.
cfg_builder = QuixKafkaConfigsBuilder()

# Get the input topic name from an environment variable
cfgs, topics, _ = cfg_builder.get_confluent_client_configs([os.environ["output"]])

# Create the topic if it doesn't yet exist
cfg_builder.create_topics([TopicCreationConfigs(name=topics[0])])

# Define a serializer for adding the extra headers
# here we are using the JSONSerializer
serializer = JSONSerializer()

# NOTE: if you have existing services in Quix, possibly using a version of the SDK before v2
# and want to subscribe to data from there, use the QuixSerializer like this:
# serializer = QuixSerializer()


brokers=cfgs.pop("bootstrap.servers")

def publish_row(stream_id: str, row_data: dict):
    global row_counter
    global published_total
    global cfgs

    # Initialize a Kafka Producer using the stream ID as the message key
    with Producer(broker_address=brokers, extra_config=cfgs) as producer:

        # serialize the row (dictionary)
        ser = serializer(value=row_data, ctx=SerializationContext(topic=topics[0]))

        producer.produce(
            topic=topics[0],
            key=stream_id,
            value=ser,
        )

    row_counter += 1

    if row_counter == 10:
        row_counter = 0
        published_total += 10
        print(f"Published {published_total} rows")
    

def process_csv_file(csv_file):
    global shutting_down

    # Read the CSV file into a pandas DataFrame
    print("CSV file loading.")

    df = pd.read_csv(csv_file)
    print("File loaded.")

    row_count = len(df)
    print(f"Publishing {row_count} rows.")

    has_timestamp_column = False

    # If the data contains a 'Timestamp'
    if "Timestamp" in df:
        has_timestamp_column = True
        # keep the original timestamp to ensure the original timing is maintained
        df = df.rename(columns={"Timestamp": "original_timestamp"})
        print("Timestamp column renamed.")


    # generate a unique stream id for this data stream
    stream_id = f"CSV_DATA_{str(random.randint(1, 100)).zfill(3)}"

    # Get the column headers as a list
    headers = df.columns.tolist()
        
    # Iterate over the rows and send them to the API
    for index, row in df.iterrows():

        # If shutdown has been requested, exit the loop.
        if shutting_down:
            break

        # Create a dictionary that includes both column headers and row values
        row_data = {header: row[header] for header in headers}
        
        # add a new timestamp column with the current data and time
        row_data['Timestamp'] = int(time.time() * 1e9)

        # publish the row via the wrapper function
        publish_row(stream_id, row_data)

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
processing_thread = threading.Thread(target=process_csv_file, args=("demo-data.csv",))
processing_thread.start()

# Run this method before shutting down.
# In this case we set a flag to tell the loops to exit gracefully.
def before_shutdown():
    global shutting_down
    print("Shutting down")

    # set the flag to True to stop the loops as soon as possible.
    shutting_down = True


print("Exiting.")
