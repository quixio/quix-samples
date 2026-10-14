import os

from quixstreams import Application
from quixstreams.sources.community.mysql_cdc_lite import MySqlCdcLiteSource

app = Application()
output_topic = app.topic(os.environ["output"], key_serializer="str")

tls = os.environ["MYSQL_TLS"]
source = MySqlCdcLiteSource(
    host=os.environ["MYSQL_HOST"],
    port=int(os.environ["MYSQL_PORT"]),
    user=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    database=os.environ["MYSQL_DATABASE"],
    table=os.environ["MYSQL_TABLE"],
    commit_interval=float(os.environ["MYSQL_COMMIT_INTERVAL"]),
    tls={"true": True, "false": False}.get(tls.lower(), tls),
    name=os.getenv("MYSQL_SOURCE_NAME"),
)
app.add_source(source, topic=output_topic)

if __name__ == "__main__":
    app.run()
