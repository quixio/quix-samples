# Import the Quix Streams modules for interacting with Kafka:
from quixstreams import Application
# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# Import additional modules as needed
import pandas as pd
import json
import random
import time
import os

# import the dotenv module to load environment variables from a file
from dotenv import load_dotenv
load_dotenv(override=False)

# Create an Application.
app = Application.Quix(
            consumer_group="demo-data-consumer-group",
            auto_offset_reset="earliest",
            auto_create_topics=True,  # Quix app has an option to auto create topics
        )

# Define the topic using the "output" environment variable
topic_name = os.getenv("output_topic", "")
if topic_name == "":
    raise ValueError("output_topic environment variable is required")

topic = app.topic(topic_name)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))
# Construct the path to the CSV file
csv_file_path = os.path.join(script_dir, "demo-data.csv")


# this function loads the file and sends each row to the publisher
def read_csv_file(file_path: str):
    """
    A function to read data from a CSV file in an endless manner.
    It returns a generator with stream_id and rows
    """

    # Read the CSV file into a pandas.DataFrame
    print("CSV file loading.")
    df = pd.read_csv(file_path)

    print("File loaded.")

    # Get the number of rows in the dataFrame for printing out later
    row_count = len(df)

    # Generate a unique ID for this data stream.
    # It will be used as a message key in Kafka
    stream_id = f"CSV_DATA_{str(random.randint(1, 100)).zfill(3)}"

    # Get the column headers as a list
    headers = df.columns.tolist()

    # Continuously loop over the data
    while True:
        # Print a message to the console for each iteration
        print(f"Publishing {row_count} rows.")

        # Iterate over the rows and convert them to
        for _, row in df.iterrows():
            # Create a dictionary that includes both column headers and row values
            # Replace NaN values with None (which will become 'null' in JSON)
            row_data = {header: (None if pd.isna(row[header]) else row[header]) for header in headers}

            # add a new timestamp column with the current data and time
            row_data["Timestamp"] = time.time_ns()

            # Yield the stream ID and the row data
            yield stream_id, row_data

        print("All rows published")

        # Wait a moment before outputting more data.
        time.sleep(1)


def main():
    """
    Read data from the CSV file and publish it to Kafka
    """

    # Create a pre-configured Producer object.
    # Producer is already setup to use Quix brokers.
    # It will also ensure that the topics exist before producing to them if
    # Application.Quix is initiliazed with "auto_create_topics=True".
    producer = app.get_producer()

    with producer:
        print("Publishing data..")
        # Iterate over the data from CSV file
        for message_key, row_data in read_csv_file(file_path=csv_file_path):
            # Serialize row_data to a JSON string
            json_data = json.dumps(row_data)
            # Encode the JSON string to a byte array
            serialized_value = json_data.encode('utf-8')
            # publish the data to the topic
            producer.produce(
                topic=topic.name,
                key=message_key,
                value=serialized_value
            )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")
