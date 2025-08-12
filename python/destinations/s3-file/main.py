from typing import get_args

from quixstreams import Application
from quixstreams.sinks.community.file.s3 import S3FileSink
from quixstreams.sinks.community.file.formats import FormatName
import os

from dotenv import load_dotenv
load_dotenv()


def get_file_format() -> FormatName:
    valid_formats = get_args(FormatName)
    if (file_format := os.getenv("FILE_FORMAT", "parquet")) not in valid_formats:
        raise ValueError(
            f"`FILE_FORMAT` must be one of {valid_formats}; got {file_format}"
        )
    return file_format


app = Application(
    consumer_group="s3-destination",
    auto_offset_reset="earliest",
    commit_interval=5
)

s3_file_sink = S3FileSink(
    bucket=os.environ["S3_BUCKET"],
    directory=os.getenv("S3_BUCKET_DIRECTORY", ""),
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    endpoint_url=os.environ["AWS_ENDPOINT_URL"],
    region_name=os.environ["AWS_REGION_NAME"],
    format=get_file_format(),
)

sdf = app.dataframe(app.topic(os.environ["input"])).sink(s3_file_sink)
sdf.sink()


if __name__ == "__main__":
    app.run()
