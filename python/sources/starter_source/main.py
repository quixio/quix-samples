from quixstreams import Application  # import the Quix Streams modules for interacting with Kafka:
# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# import additional modules as needed
import random
import os
import json

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application.Quix(consumer_group="data_source", auto_create_topics=True)  # create an Application

# define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)


# this function loads the file and sends each row to the publisher
def get_data():
    """
    A function to generate data from a hardcoded dataset in an endless manner.
    It returns a list of tuples with a message_key and rows
    """

    # define the hardcoded dataset
    # this data is fake data representing used % of memory allocation over time
    # there is one row of data every 1 to 2 seconds
    data = [
        {"m": "mem", "host": "host1", "used_percent": "64.56", "time": "1577836800000000000"},
        {"m": "mem", "host": "host2", "used_percent": "71.89", "time": "1577836801000000000"},
        {"m": "mem", "host": "host1", "used_percent": "63.27", "time": "1577836803000000000"},
        {"m": "mem", "host": "host2", "used_percent": "73.45", "time": "1577836804000000000"},
        {"m": "mem", "host": "host1", "used_percent": "62.98", "time": "1577836806000000000"},
        {"m": "mem", "host": "host2", "used_percent": "74.33", "time": "1577836808000000000"},
        {"m": "mem", "host": "host1", "used_percent": "65.21", "time": "1577836810000000000"},
        {"m": "mem", "host": "host2", "used_percent": "70.88", "time": "1577836812000000000"},
        {"m": "mem", "host": "host1", "used_percent": "64.61", "time": "1577836814000000000"},
        {"m": "mem", "host": "host2", "used_percent": "72.56", "time": "1577836816000000000"},
        {"m": "mem", "host": "host1", "used_percent": "63.77", "time": "1577836818000000000"},
        {"m": "mem", "host": "host2", "used_percent": "73.21", "time": "1577836820000000000"}
    ]

    # create a list of tuples with row_data
    data_with_id = [(row_data) for row_data in data]

    return data_with_id


def main():
    """
    Read data from the hardcoded dataset and publish it to Kafka
    """

    # create a pre-configured Producer object.
    with app.get_producer() as producer:
        # iterate over the data from the hardcoded dataset
        data_with_id = get_data()
        for row_data in data_with_id:

            json_data = json.dumps(row_data)  # convert the row to JSON

            # publish the data to the topic
            producer.produce(
                topic=topic.name,
                key=row_data['host'],
                value=json_data,
            )

            # for more help using QuixStreams see docs:
            # https://quix.io/docs/quix-streams/introduction.html

        print("All rows published")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")