import os
import traceback
from quixstreams import Application
from quixstreams.sources.core.kafka import QuixEnvironmentSource
from dotenv import load_dotenv

def main():
    app = Application()
    
    # Load environment variables from .env file for local development
    load_dotenv()
    
    # Setup output topic
    output_topic = app.topic(os.environ["topic"])

    # Get necessary environment variables for Quix input topic
    source_workspace_id = os.environ["source_workspace_id"]
    source_sdk_token = os.environ["source_sdk_token"]

    # Setup input topic
    input_topic = QuixEnvironmentSource(
        name="quix-environment-source",
        app_config=app.config,
        topic=os.environ["topic"],
        quix_sdk_token=source_sdk_token,
        quix_workspace_id=source_workspace_id
    )

    app.add_source(input_topic, output_topic)
    print("CONNECTED!")

    # Start the application
    app._run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR! - An error occurred in the application.")
        traceback.print_exc()
        if 'app' in locals():  # Ensure app exists before stopping it
            app.stop()