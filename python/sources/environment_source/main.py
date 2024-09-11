import os
import traceback
from quixstreams import Application
from quixstreams.sources.kafka import QuixEnvironmentSource
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file for local development
    load_dotenv()

    app = Application()
    
    # Setup output topic
    output_topic = app.topic(os.environ["output"])

    # Get necessary environment variables for Quix input topic
    source_workspace_id = os.environ["source_workspace_id"]
    source_sdk_token = os.environ["source_sdk_token"]
    consumer_group = os.environ["consumer_group"]
    auto_offset_reset = os.environ["auto_offset_reset"]

    # Setup input topic
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

    # Create a streaming dataframe
    sdf = app.dataframe(source=input_topic)

    print("CONNECTED")
    # Uncomment if needed for debugging
    # sdf.print()
    # sdf.to_topic(output_topic)

    # Start the application
    app.run(sdf)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR: An error occurred in the application.")
        traceback.print_exc()
        if 'app' in locals():  # Ensure app exists before stopping it
            app.stop()