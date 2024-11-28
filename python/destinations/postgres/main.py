import os
from quixstreams import Application
from postgres_sink import PostgresSink

# Load environment variables from a .env file for local development
from dotenv import load_dotenv
load_dotenv()

# Initialize PostgreSQL Sink
postgres_sink = PostgresSink(
    host=os.environ["POSTGRES_HOST"],
    port=int(os.environ["POSTGRES_PORT"]),
    dbname=os.environ["POSTGRES_DBNAME"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    table_name=os.environ["POSTGRES_TABLE"],
    schema_auto_update=os.environ.get("SCHEMA_AUTO_UPDATE", "true").lower() == "true"
)

# Buffer settings
buffer_size = int(os.environ.get("BATCH_SIZE", "1000"))
buffer_delay = float(os.environ.get("BATCH_TIMEOUT", "1"))

# Initialize the application
app = Application(
    consumer_group=os.environ["CONSUMER_GROUP_NAME"],
    auto_offset_reset="earliest",
    commit_interval=buffer_delay,
    commit_every=buffer_size
)

# Define the input topic
input_topic = app.topic(os.environ["input"], key_deserializer="string")

# Process and sink data
sdf = app.dataframe(input_topic)
sdf.sink(postgres_sink)

if __name__ == "__main__":
    app.run(sdf)