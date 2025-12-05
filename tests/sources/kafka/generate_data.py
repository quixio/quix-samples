import datetime

from quixstreams.sources.community.file.local import LocalFileSource
from quixstreams import Application


def ts_setter(row):
    return int(datetime.datetime.now().timestamp())


app = Application(
    broker_address="external-kafka:9092",
    auto_offset_reset="earliest"
)
app.add_source(
    source=LocalFileSource(filepath="./data.jsonlines", timestamp_setter=ts_setter),
    topic=app.topic("original-topic"),
)

if __name__ == "__main__":
    app.run()
