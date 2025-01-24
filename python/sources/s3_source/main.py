from quixstreams import Application
from quixstreams.sources.community.file import FileSource
from quixstreams.sources.community.file.origins import S3Origin

import os
from dotenv import load_dotenv
load_dotenv()

app = Application()

# create an output topic
output_topic = app.topic(os.environ['output'])

# describe the file origin and access credentials
origin = S3Origin(
    bucket=os.environ['s3_bucket'],
    aws_access_key_id=os.environ['s3_access_key_id'],
    aws_secret_access_key=os.environ['s3_secret'],
    region_name=os.environ['s3_region'],
)

# create a file source, describing the file path and formats
source = FileSource(
    directory=os.environ['s3_folder_path'],
    origin=origin,
    format=os.environ['s3_file_format'],
    compression=os.environ['s3_file_compression'],
)

app.add_source(source)

if __name__ == "__main__":
    app.run()