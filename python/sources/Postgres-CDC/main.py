from quixstreaming import QuixStreamingClient
import time
import datetime
import os
import json
from setup_logger import logger
from postgres_helper import connect_postgres, create_logical_slot, create_publication_on_table, get_changes

#Global Variables
PG_SLOT_NAME = "replication_slot"
PG_PUBLICATION_NAME = "pub"
PG_SCHEMA = os.environ["PG_SCHEMA"]
PG_TABLE = os.environ["PG_TABLE"]
PG_TABLE_NAME = "{PG_SCHEMA}.{PG_TABLE}"
WAIT_INTERVAL = 0.1
# Connect to postgres and set up table
try:
    create_logical_slot(PG_SLOT_NAME)
    create_publication_on_table(PG_PUBLICATION_NAME, PG_TABLE_NAME)
    conn = connect_postgres()
except:
    # End program or something
    pass


# Quix injects credentials automatically to the client. Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()

# Open the output topic where to write data out
output_topic = client.open_output_topic(os.environ["output"])

stream = output_topic.create_stream()
stream.properties.name = f"{PG_TABLE_NAME} CDC"
stream.parameters.add_definition("cdc_data")
stream.parameters.buffer.time_span_in_milliseconds = 100

logger.info(f"Start stream CDC for table: {PG_TABLE_NAME}")
while True:
    records = get_changes(conn, PG_SLOT_NAME)
    for record in records:
        changes = json.loads(record[0])
        for change in changes["change"]:
            logger.debug(json.dumps(change))
            stream.parameters \
                .buffer \
                .add_timestamp(datetime.datetime.utcnow()) \
                .add_value("cdc_data", json.dumps(change)) \
                .write()
    time.sleep(WAIT_INTERVAL)

logger.info("Closing stream")
stream.close()