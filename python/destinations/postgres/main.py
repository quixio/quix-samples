import os
from quixstreams import Application
from quixstreams.sinks.community.postgresql import PostgreSQLSink
# Load environment variables from a .env file for local development
from dotenv import load_dotenv
load_dotenv()

# Initialize PostgreSQL Sink
postgres_sink = PostgreSQLSink(
    host=os.environ["POSTGRES_HOST"],
    port=int(os.environ["POSTGRES_PORT"]),
    dbname=os.environ["POSTGRES_DBNAME"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    table_name=os.environ["POSTGRES_TABLE"],
    schema_name=os.getenv("POSTGRES_SCHEMA", "public"),
    schema_auto_update=os.environ.get("SCHEMA_AUTO_UPDATE", "true").lower() == "true",
)

# Initialize the application
app = Application(
    consumer_group=os.environ["CONSUMER_GROUP_NAME"],
    auto_offset_reset="earliest",
    commit_interval=float(os.environ.get("BATCH_TIMEOUT", "1")),
    commit_every=int(os.environ.get("BATCH_SIZE", "1000"))
)

# Define the input topic
input_topic = app.topic(os.environ["input"], key_deserializer="string")

# Process and sink data
sdf = app.dataframe(input_topic)
sdf.sink(postgres_sink)

if __name__ == "__main__":
    app.run(sdf)