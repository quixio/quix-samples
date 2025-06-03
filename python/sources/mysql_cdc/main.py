from quixstreams import Application
import time
import os
import json
from setup_logger import logger
from mysql_helper import connect_mysql, enable_binlog_if_needed, setup_mysql_cdc, create_binlog_stream, get_changes, perform_initial_snapshot, save_binlog_position

# Load environment variables (useful when working locally)
from dotenv import load_dotenv
load_dotenv()

# Global Variables
MYSQL_SCHEMA = os.environ["MYSQL_SCHEMA"]  # MySQL database name
MYSQL_TABLE = os.environ["MYSQL_TABLE"]    # MySQL table name
MYSQL_TABLE_NAME = f"{MYSQL_SCHEMA}.{MYSQL_TABLE}"
WAIT_INTERVAL = 0.1

# Initial snapshot configuration
INITIAL_SNAPSHOT = os.getenv("INITIAL_SNAPSHOT", "false").lower() == "true"
SNAPSHOT_BATCH_SIZE = int(os.getenv("SNAPSHOT_BATCH_SIZE", "1000"))
FORCE_SNAPSHOT = os.getenv("FORCE_SNAPSHOT", "false").lower() == "true"

# State management - use Quix state dir if available, otherwise default to "state"
STATE_DIR = os.getenv("Quix__State__Dir", "state")
SNAPSHOT_STATE_FILE = os.path.join(STATE_DIR, f"snapshot_completed_{MYSQL_SCHEMA}_{MYSQL_TABLE}.flag")

def ensure_state_dir():
    """Create state directory if it doesn't exist"""
    if not os.path.exists(STATE_DIR):
        os.makedirs(STATE_DIR)
        logger.info(f"Created state directory: {STATE_DIR}")

def is_snapshot_completed():
    """Check if initial snapshot has been completed"""
    return os.path.exists(SNAPSHOT_STATE_FILE) and not FORCE_SNAPSHOT

def mark_snapshot_completed():
    """Mark initial snapshot as completed"""
    ensure_state_dir()
    with open(SNAPSHOT_STATE_FILE, 'w') as f:
        f.write(json.dumps({
            "completed_at": time.time(),
            "schema": MYSQL_SCHEMA,
            "table": MYSQL_TABLE,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }))
    logger.info(f"Snapshot completion marked in: {SNAPSHOT_STATE_FILE}")

def get_snapshot_info():
    """Get information about when snapshot was completed"""
    if os.path.exists(SNAPSHOT_STATE_FILE):
        try:
            with open(SNAPSHOT_STATE_FILE, 'r') as f:
                return json.loads(f.read())
        except:
            return None
    return None

# Create a Quix Application, this manages the connection to the Quix platform
app = Application()

# Connect to MySQL and set up CDC
try:
    enable_binlog_if_needed()
    setup_mysql_cdc(MYSQL_TABLE)
    conn = connect_mysql()
    binlog_stream = create_binlog_stream()
    logger.info("MySQL CDC CONNECTED!")
except Exception as e:
    logger.error(f"ERROR! - {e}")
    raise

# should the main loop run?
run = True

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

    # Perform initial snapshot if enabled and not already completed
    if INITIAL_SNAPSHOT:
        if is_snapshot_completed():
            snapshot_info = get_snapshot_info()
            if FORCE_SNAPSHOT:
                logger.info("Initial snapshot already completed but FORCE_SNAPSHOT=true - performing snapshot again...")
            else:
                logger.info(f"Initial snapshot already completed at {snapshot_info.get('timestamp', 'unknown time')} - skipping")
        else:
            logger.info("Initial snapshot is enabled and not yet completed - performing snapshot...")
        
        if not is_snapshot_completed():
            try:
                snapshot_changes = perform_initial_snapshot(MYSQL_SCHEMA, MYSQL_TABLE, SNAPSHOT_BATCH_SIZE)
                
                # Send snapshot data to Kafka immediately
                for change in snapshot_changes:
                    producer.produce(topic=output_topic.name,
                                    key=MYSQL_TABLE_NAME,
                                    value=json.dumps(change))
                
                # Flush to ensure all snapshot data is sent
                producer.flush()
                logger.info(f"Initial snapshot completed - {len(snapshot_changes)} records sent to Kafka")
                
                # Mark snapshot as completed
                mark_snapshot_completed()
                
            except Exception as e:
                logger.error(f"Failed to perform initial snapshot: {e}")
                raise
    else:
        logger.info("Initial snapshot is disabled - starting CDC stream only")

    # Start CDC loop
    while run:
        # Get changes from MySQL binlog
        changes = get_changes(binlog_stream, MYSQL_SCHEMA, MYSQL_TABLE)
        for change in changes:
            buffer.append(change)
        
        if len(buffer) > 0:
            print(f"Buffer length: {len(buffer)}")
            print(f"Buffer: {buffer}")
        
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
            producer.flush()
            
            # Save binlog position after successful send
            if hasattr(binlog_stream, 'log_file') and hasattr(binlog_stream, 'log_pos'):
                save_binlog_position(binlog_stream.log_file, binlog_stream.log_pos)
                
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
        if 'conn' in locals():
            conn.close()
        if 'binlog_stream' in locals():
            binlog_stream.close()
        logger.info("Connection to MySQL closed")
        logger.info("Exiting")