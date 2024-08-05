from csv_source import CsvSource
from quixstreams import Application
import os

# import the dotenv module to load environment variables from a file
from dotenv import load_dotenv
load_dotenv(override=False)

# Create an Application.
app = Application()

# Define the topic using the "output" environment variable
topic_name = os.getenv("output", "")
if topic_name == "":
    raise ValueError("The 'output' environment variable is required. This is the output topic that data will be published to.")

csv_source = CsvSource("demo-data.csv", sleep_between_rows=0.2)
sdf = app.dataframe(source=csv_source)
output_topic = app.topic(topic_name)

sdf.print()
sdf.to_topic(output_topic)


if __name__ == "__main__": 
    app.run(sdf)