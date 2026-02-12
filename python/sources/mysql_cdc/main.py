import os
import logging
from dotenv import load_dotenv

from quixstreams import Application
from quixstreams.sources.community.mysql_cdc import MySqlCdcSource

load_dotenv()

logger = logging.getLogger(__name__)

app = Application(
    consumer_group=os.getenv("CONSUMER_GROUP", "mysql_cdc"),
)
output_topic = app.topic(os.environ["output"])
mysql_source = MySqlCdcSource(
    host=os.environ["MYSQL_HOST"],
    port=os.environ["MYSQL_PORT"],
    user=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    database=os.environ["MYSQL_DATABASE"],
    table=os.environ["MYSQL_TABLE"],
    initial_snapshot=os.getenv("MYSQL_INITIAL_SNAPSHOT", "false").lower() == "true",
    snapshot_host=os.getenv("MYSQL_SNAPSHOT_HOST") or None,
    snapshot_batch_size=int(os.getenv("MYSQL_SNAPSHOT_BATCH_SIZE", 1000)),
    force_snapshot=os.getenv("MYSQL_FORCE_SNAPSHOT", "false").lower() == "true",
)
app.add_source(mysql_source, output_topic)


def main():
    app.run()


if __name__ == "__main__":
    main()