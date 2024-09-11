import os
import traceback
from quixstreams import Application
from quixstreams.sources.kafka import QuixEnvironmentSource

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application()
output_topic = app.topic(os.environ["output"])

source_workspace_id = os.environ["source_workspace_id"]
source_sdk_token = os.environ["source_sdk_token"]
consumer_group = os.environ["consumer_group"]
auto_offset_reset = os.environ["auto_offset_reset"]

input_topic = QuixEnvironmentSource(
    output_topic.name,
    app.config,
    output_topic.name,
    quix_workspace_id=source_workspace_id, 
    quix_sdk_token=source_sdk_token,
    consumer_group=consumer_group,
    auto_offset_reset=auto_offset_reset,
    shutdown_timeout=30
)

sdf = app.dataframe(source=input_topic)


print("CONNECTED")
#sdf.print()
#sdf.to_topic(output_topic)

if __name__ == "__main__":
    try:
        app.run(sdf)
    except Exception as e:
        print("ERROR: Application failed to run.")
        traceback.print_exc()
        app.stop()