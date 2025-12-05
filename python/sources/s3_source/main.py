from quixstreams import Application
from quixstreams.sources.community.file.s3 import S3FileSource
import time

import os
from dotenv import load_dotenv
load_dotenv()

app = Application()

# create an output topic
output_topic = app.topic(os.environ['output'])

# Custom setters for S3 file records (must be regular functions for pickling)
def key_setter(row):
    """Use record ID as the message key, or None if not present."""
    return str(row.get('id', '')) if 'id' in row else None

def value_setter(row):
    """Use the whole record as the message value."""
    return row

def timestamp_setter(row):
    """Use current time as message timestamp."""
    return int(time.time() * 1000)

# Build S3FileSource kwargs
source_kwargs = {
    'filepath': os.environ['S3_FOLDER_PATH'],
    'bucket': os.environ['S3_BUCKET'],
    'aws_access_key_id': os.environ['S3_ACCESS_KEY_ID'],
    'aws_secret_access_key': os.environ['S3_SECRET'],
    'region_name': os.environ['S3_REGION'],
    'file_format': os.environ['S3_FILE_FORMAT'],
    'compression': os.environ.get('S3_FILE_COMPRESSION'),
    'key_setter': key_setter,
    'value_setter': value_setter,
    'timestamp_setter': timestamp_setter,
}

# Support custom endpoint for MinIO or other S3-compatible services
if 'S3_ENDPOINT_URL' in os.environ:
    source_kwargs['endpoint_url'] = os.environ['S3_ENDPOINT_URL']

# create the S3 file source
source = S3FileSource(**source_kwargs)

app.add_source(source, topic=output_topic)

if __name__ == "__main__":
    app.run()