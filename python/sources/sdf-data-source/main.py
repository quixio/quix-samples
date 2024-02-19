from quixstreams import Application  # Import the Quix Streams modules for interacting with Kafka:
# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# Import additional modules as needed
import random
import os
from dotenv import load_dotenv
import json


with open("./.env", 'a+') as file: pass  # make sure the .env file exists
load_dotenv("./.env")

app = Application.Quix(consumer_group="data_source", auto_create_topics=True)  # Create an Application


# Define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)


# this function loads the file and sends each row to the publisher
def read_csv_file():
    """
    A function to generate data from a hardcoded dataset in an endless manner.
    It returns a list of tuples with stream_id and rows
    """

    # Define the hardcoded dataset
    data = [
        {"Timestamp": 1687516100000000000, "Number": 1, "Name": "Scarlett"},
        {"Timestamp": 1687516095000000000, "Number": 2, "Name": "Charles"},
        {"Timestamp": 1687516100000000000, "Number": 3, "Name": "James"},
        {"Timestamp": 1687516095000000000, "Number": 4, "Name": "Amelia"},
        {"Timestamp": 1687516100000000000, "Number": 5, "Name": "Grace"},
    ]

    # Generate a unique ID for this data stream.
    # It will be used as a message key in Kafka
    stream_id = f"CSV_DATA_{str(random.randint(1, 100)).zfill(3)}"

    # Create a list of tuples with stream_id and row_data
    data_with_id = [(stream_id, row_data) for row_data in data]

    return data_with_id


def main():
    """
    Read data from the hardcoded dataset and publish it to Kafka
    """

    # Create a pre-configured Producer object.
    producer = app.get_producer()

    with producer:
        # Iterate over the data from the hardcoded dataset
        data_with_id = read_csv_file()
        for message_key, row_data in data_with_id:

            json_data = json.dumps(row_data)  # convert the row to JSON

            # publish the data to the topic
            producer.produce(
                topic=topic.name,
                key=message_key,
                value=json_data,
            )

        print("All rows published")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")