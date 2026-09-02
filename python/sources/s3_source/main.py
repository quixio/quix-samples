import os
import logging
from quixstreams import Application
from s3_file_watcher import S3FileWatcher
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
def conn_var(new_name: str, legacy_name: str, default: str = None) -> str:
    """
    Read a connection env var by the name the shared aws-connection Variable Group
    injects, falling back to the legacy name so deployments created before the rename
    keep working.
    """
    value = os.getenv(new_name) or os.getenv(legacy_name) or default
    if value is None:
        raise KeyError(f"{new_name} (or legacy {legacy_name})")
    return value


# Credentials, region and endpoint come from the shared aws-connection Variable Group,
# falling back to the legacy S3_* names so existing deployments keep working. These two
# stay optional (`or None`): S3FileWatcher falls back to the ambient credential chain -
# an IAM role, or anonymous access - when neither is supplied.
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("S3_ACCESS_KEY_ID") or None
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv("S3_SECRET") or None
S3_BUCKET_NAME = os.environ["S3_BUCKET"]
S3_FOLDER_PREFIX = os.getenv("S3_FOLDER_PREFIX", "")
AWS_REGION = conn_var("AWS_REGION", "S3_REGION", "us-east-1")
# For MinIO or custom S3-compatible endpoints. `or None` so a blank value from the
# Variable Group is not passed to boto3 as an empty endpoint URL.
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL") or None
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
    endpoint_url=AWS_ENDPOINT_URL,
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