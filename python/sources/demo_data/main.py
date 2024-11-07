import os
import random

# import the dotenv module to load environment variables from a file
from dotenv import load_dotenv
from quixstreams import Application
from quixstreams.sources.core.csv import CSVSource

load_dotenv(override=False)

# Create an Application.
app = Application()

# Define the topic using the "output" environment variable
topic_name = os.getenv("output")
if topic_name is None:
    raise ValueError(
        "The 'output' environment variable is required. This is the output topic that data will be published to."
    )

# Specify the filename here
filename = "demo-data.csv"

message_key = f"{filename}_{str(random.randint(1, 100)).zfill(3)}"


def key_extractor(row: dict) -> str:
    """
    Generate a random message key for each source run
    """
    return message_key


def timestamp_extractor(row: dict) -> int:
    """
    Extract a timestamp from each row and use it as a Kafka message timestamp
    """
    return int(row["Timestamp"] / 1_000_000)


csv_source = CSVSource(
    path=filename,
    name="csv",
    key_extractor=key_extractor,
    timestamp_extractor=timestamp_extractor,
    delay=0.2,
)
sdf = app.dataframe(source=csv_source)
output_topic = app.topic(topic_name)

sdf.print(metadata=True)
sdf.to_topic(output_topic)


if __name__ == "__main__":
    app.run(sdf)
