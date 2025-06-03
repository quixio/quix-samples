from quixstreams import Application
import time
import os
import json
from setup_logger import logger
from mysql_helper import connect_mysql, enable_binlog_if_needed, setup_mysql_cdc, create_binlog_stream, get_changes

# Load environment variables (useful when working locally)
from dotenv import load_dotenv
load_dotenv()

# Global Variables
MYSQL_SCHEMA = os.environ["MYSQL_SCHEMA"]  # MySQL database name
MYSQL_TABLE = os.environ["MYSQL_TABLE"]    # MySQL table name
MYSQL_TABLE_NAME = f"{MYSQL_SCHEMA}.{MYSQL_TABLE}"
WAIT_INTERVAL = 0.1

# Connect to MySQL and set up CDC
try:
    enable_binlog_if_needed()
    setup_mysql_cdc(MYSQL_TABLE)
    conn = connect_mysql()
    binlog_stream = create_binlog_stream()
    logger.info("MySQL CDC CONNECTED!")
except Exception as e:
    logger.info(f"ERROR! - {e}")
    raise

# should the main loop run?
run = True

# Create a Quix Application, this manages the connection to the Quix platform
app = Application()

# Create the producer, this is used to write data to the output topic
producer = app.get_producer()

# Check the output topic is configured
output_topic_name = os.getenv("output", "")
if output_topic_name == "":
    raise ValueError("output_topic environment variable is required")
output_topic = app.topic(output_topic_name)

# get data from MySQL binlog and publish it to kafka
# to reduce network traffic, we buffer the messages for 500ms
def main():
    buffer = []
    last_flush_time = time.time()

    while run:
        # Get changes from MySQL binlog
        changes = get_changes(binlog_stream, MYSQL_SCHEMA, MYSQL_TABLE)
        for change in changes:
            buffer.append(change)
                
        # Check if 500 milliseconds have passed
        current_time = time.time()
        if (current_time - last_flush_time) >= 0.5 and len(buffer) > 0:
            # If 500ms have passed, produce all buffered messages
            for message in buffer:
                producer.produce(topic=output_topic.name,
                                    key=MYSQL_TABLE_NAME,
                                    value=json.dumps(message))
                print("Message sent to Kafka")
                # Flush the producer to send the messages
                
            # Clear the buffer
            buffer = []
            # Update the last flush time
            last_flush_time = current_time

        time.sleep(WAIT_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Exiting.")
        run = False
    finally:
        conn.close()
        binlog_stream.close()
        logger.info("Connection to MySQL closed")
        logger.info("Exiting")