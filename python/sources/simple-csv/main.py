# Import the Quix Streams modules for interacting with Kafka: 
from quixstreams import Application
from quixstreams.models.serializers.quix import JSONSerializer, SerializationContext
# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# Import additional modules as needed
import pandas as pd
import random
import time
import os

# Create an Application.
# Consumer group is irrelevant for Producer and is a random string here
app = Application.Quix(consumer_group="csv_sample", auto_create_topics=True)
# Define a serializer for messages, using JSON Serializer for ease
serializer = JSONSerializer()

# get the topic name from the 'output' environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

# Create a pre-configured Producer object.
# Producer is already setup to use Quix brokers.
# It will also ensure that the topics are created before producing to them if
# Application.Quix is initiliazed with "auto_create_topics=True".
producer = app.get_producer()

# wrap the Quix producer code in a function
def publish_row(stream_id: str, row_data: dict):
   
    # Serialize value to bytes
    serialized_value = serializer(
        value=row_data,
        ctx=SerializationContext(topic=topic.name)
    )

    # publish the data to the topic
    producer.produce(
        topic=topic.name,
        key=stream_id,
        value=serialized_value,
    )


# this function loads the file and sends each row to the publisher
def process_csv_file(csv_file):

    # Read the CSV file into a pandas DataFrame
    print("CSV file loading.")
    df = pd.read_csv(csv_file)
    print("File loaded.")

    # Get the number of rows in the dataFrame for printing out later
    row_count = len(df)

    # Generate a unique stream id for this data stream
    stream_id = f"CSV_DATA_{str(random.randint(1, 100)).zfill(3)}"

    # Get the column headers as a list
    headers = df.columns.tolist()
    
    # Continuously loop over the data
    while True:

        # Print a message to the console for each iteration
        print(f"Publishing {row_count} rows.")

        # Iterate over the rows and send them to the API
        for index, row in df.iterrows():

            # Create a dictionary that includes both column headers and row values
            row_data = {header: row[header] for header in headers}
            
            # add a new timestamp column with the current data and time
            row_data['Timestamp'] = int(time.time() * 1e9)

            # publish the row via the wrapper function
            publish_row(stream_id, row_data)

            # wait a moment after publishing the last row.
            time.sleep(0.5)

        print("All rows published")
        
        # Wait a moment before publishing more data.
        time.sleep(1)


# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the file
file_path = os.path.join(script_dir, 'demo-data.csv')

# start the process
process_csv_file(file_path)

print("Exiting.")
