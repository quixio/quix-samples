import os
import logging
from quixstreams import Application
from s3_file_watcher import S3FileWatcher
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AWS_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("S3_SECRET")
S3_BUCKET_NAME = os.environ["S3_BUCKET"]
S3_FOLDER_PREFIX = os.getenv("S3_FOLDER_PREFIX", "")
AWS_REGION = os.getenv("S3_REGION", "us-east-1")
TOPIC_NAME = os.environ["output"]
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Quix Application
app = Application(consumer_group="s3_file_watcher_v1.2", auto_create_topics=True)

# Create S3 File Watcher Source
s3_file_watcher = S3FileWatcher(
    name="s3_file_watcher",
    bucket_name=S3_BUCKET_NAME,
    folder_prefix=S3_FOLDER_PREFIX,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
    poll_interval=POLL_INTERVAL
)

# Define the topic using the "output" environment variable
topic = app.topic(TOPIC_NAME)

# Add source to application
app.add_source(s3_file_watcher, topic)

if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        app.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting gracefully.")