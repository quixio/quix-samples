# import Utility modules
import os

# import vendor-specific modules
from quixstreams import Application
from quixstreams.sinks.community.tdengine.sink import TDengineSink

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()


tag_keys = keys.split(",") if (keys := os.environ.get("TDENGINE_TAG_KEYS")) else []
field_keys = keys.split(",") if (keys := os.environ.get("TDENGINE_FIELD_KEYS")) else []
time_setter = col if (col := os.environ.get("TIMESTAMP_COLUMN")) else None

tdengine_sink = TDengineSink(
    token=os.environ["TDENGINE_TOKEN"],
    host=os.environ["TDENGINE_HOST"],
    tags_keys=tag_keys,
    fields_keys=field_keys,
    time_setter=time_setter,
    database=os.environ["TDENGINE_DATABASE"],
    measurement=os.environ["TDENGINE_SUPERTABLE"],
)


app = Application(
    consumer_group=os.environ.get("CONSUMER_GROUP_NAME", "tdengine-data-writer"),
    auto_offset_reset="earliest",
    commit_every=int(os.environ.get("BUFFER_SIZE", "1000")),
    commit_interval=float(os.environ.get("BUFFER_DELAY", "1")),
)
input_topic = app.topic(os.environ["input"])
app.dataframe(input_topic).sink(tdengine_sink)


if __name__ == "__main__":
    app.run()
