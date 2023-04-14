import quixstreams as qx
import time
import datetime
import os
import json
from setup_logger import logger
from threading import Thread
from postgres_helper import connect_postgres, create_logical_slot, create_publication_on_table, get_changes

#Global Variables
PG_SLOT_NAME = "replication_slot"
PG_SCHEMA = os.environ["PG_SCHEMA"]
PG_TABLE = os.environ["PG_TABLE"]
PG_PUBLICATION_NAME = f"pub_{PG_SCHEMA}_{PG_TABLE}"
PG_TABLE_NAME = f"{PG_SCHEMA}.{PG_TABLE}"
WAIT_INTERVAL = 0.1
# Connect to postgres and set up table
try:
    create_logical_slot(PG_SLOT_NAME)
    create_publication_on_table(PG_PUBLICATION_NAME, PG_TABLE_NAME)
    conn = connect_postgres()
    logger.info("CONNECTED!")
except Exception as e:
    logger.info(f"ERROR!: {e}")
    raise

# should the main loop run?
run = True

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = qx.QuixStreamingClient()

# Open the output topic where to write data out
producer_topic = client.get_topic_producer(os.environ["output"])

stream = producer_topic.create_stream()
stream.properties.name = f"{PG_TABLE_NAME} CDC"
stream.timeseries.add_definition("cdc_data")
stream.timeseries.buffer.time_span_in_milliseconds = 100

def get_data():
    logger.info(f"Start stream CDC for table: {PG_TABLE_NAME}")
    while run:
        records = get_changes(conn, PG_SLOT_NAME)
        for record in records:
            changes = json.loads(record[0])
            for change in changes["change"]:
                logger.debug(json.dumps(change))
                stream.events \
                    .add_timestamp(datetime.datetime.utcnow()) \
                    .add_value("cdc_data", json.dumps(change)) \
                    .publish()
        time.sleep(WAIT_INTERVAL)


def before_shutdown():
    global run

    # Stop the main loop
    run = False


def main():
    thread = Thread(target = get_data)
    thread.start()

    qx.App.run(before_shutdown = before_shutdown)

    # wait for worker thread to end
    thread.join()

    print("Exiting")


if __name__ == "__main__":
    main()
