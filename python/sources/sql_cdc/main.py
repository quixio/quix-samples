"""
SQL Server CDC Source

Streams change data from SQL Server using native Change Data Capture (CDC).

This connector reads from SQL Server CDC change tables to capture INSERT, UPDATE,
and DELETE operations in near real-time.

Requirements:
- CDC must be enabled on the SQL Server database and target table
- User must have appropriate CDC permissions
"""
from quixstreams import Application
import os
import json
import time
import logging
from typing import Optional
from dotenv import load_dotenv

import cdc_helper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
SQL_SERVER = os.environ["SQL_SERVER"]
SQL_DATABASE = os.environ["SQL_DATABASE"]
SQL_USERNAME = os.environ["SQL_USERNAME"]
SQL_PASSWORD = os.environ["SQL_PASSWORD"]
SQL_DRIVER = os.getenv("SQL_DRIVER", "{ODBC Driver 18 for SQL Server}")
SQL_SCHEMA = os.getenv("SQL_SCHEMA", "dbo")
SQL_TABLE = os.environ["SQL_TABLE"]
OUTPUT_TOPIC = os.environ["output"]
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "5"))

# LSN state file for persistence
STATE_FILE = os.getenv("STATE_FILE", "/tmp/sql_cdc_state.json")


def load_last_lsn() -> Optional[bytes]:
    """
    Load the last processed LSN from state file.

    Returns:
        Last LSN as bytes, or None if no state exists
    """
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                lsn_hex = state.get('last_lsn')
                if lsn_hex:
                    logger.info(f"Loaded last LSN from state: {lsn_hex}")
                    return cdc_helper.hex_to_lsn(lsn_hex)
    except Exception as e:
        logger.warning(f"Failed to load LSN state: {e}")

    return None


def save_last_lsn(lsn: bytes) -> None:
    """
    Save the last processed LSN to state file.

    Args:
        lsn: LSN to save
    """
    try:
        lsn_hex = cdc_helper.lsn_to_hex(lsn)
        state = {'last_lsn': lsn_hex}

        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)

        logger.debug(f"Saved LSN state: {lsn_hex}")
    except Exception as e:
        logger.error(f"Failed to save LSN state: {e}")


def main():
    """Main CDC processing loop."""
    logger.info("Starting SQL Server CDC Source")
    logger.info(f"Target: {SQL_SERVER}/{SQL_DATABASE}.{SQL_SCHEMA}.{SQL_TABLE}")

    # Connect to SQL Server
    try:
        conn = cdc_helper.connect_sql_server(
            server=SQL_SERVER,
            database=SQL_DATABASE,
            username=SQL_USERNAME,
            password=SQL_PASSWORD,
            driver=SQL_DRIVER
        )
        logger.info("Connected to SQL Server")
    except Exception as e:
        logger.error(f"Failed to connect to SQL Server: {e}")
        raise

    # Verify CDC is enabled
    try:
        if not cdc_helper.is_cdc_enabled(conn, SQL_SCHEMA, SQL_TABLE):
            raise ValueError(
                f"CDC is not enabled on table {SQL_SCHEMA}.{SQL_TABLE}. "
                f"Enable CDC with: EXEC sys.sp_cdc_enable_table @source_schema='{SQL_SCHEMA}', "
                f"@source_name='{SQL_TABLE}', @role_name=NULL"
            )
        logger.info(f"CDC is enabled on {SQL_SCHEMA}.{SQL_TABLE}")
    except Exception as e:
        logger.error(f"CDC verification failed: {e}")
        conn.close()
        raise

    # Initialize Quix Application
    app = Application()
    producer = app.get_producer()
    output_topic = app.topic(OUTPUT_TOPIC)

    logger.info(f"Publishing to topic: {OUTPUT_TOPIC}")

    # Get starting LSN
    last_lsn = load_last_lsn()

    if last_lsn is None:
        # Start from minimum LSN if no state exists
        last_lsn = cdc_helper.get_min_lsn(conn, SQL_SCHEMA, SQL_TABLE)
        logger.info(f"Starting from minimum LSN: {cdc_helper.lsn_to_hex(last_lsn)}")
    else:
        logger.info(f"Resuming from last LSN: {cdc_helper.lsn_to_hex(last_lsn)}")

    # Main CDC loop
    try:
        changes_processed = 0
        while True:
            try:
                # Get changes since last LSN
                changes = cdc_helper.get_changes(
                    conn=conn,
                    schema=SQL_SCHEMA,
                    table=SQL_TABLE,
                    from_lsn=last_lsn,
                    row_filter='all'
                )

                if changes:
                    logger.info(f"Processing {len(changes)} change(s)")

                    # Track the last LSN in this batch (before formatting removes it)
                    last_change_lsn = changes[-1]['__$start_lsn']

                    for change in changes:
                        # Format change event
                        event = cdc_helper.format_change_event(change.copy())

                        # Use primary key or row identifier as message key
                        # Default to table name if no ID available
                        message_key = f"{SQL_SCHEMA}.{SQL_TABLE}"
                        if 'id' in event['data']:
                            message_key = f"{message_key}:{event['data']['id']}"

                        # Publish to Kafka
                        producer.produce(
                            topic=output_topic.name,
                            key=message_key,
                            value=json.dumps(event, default=str)
                        )

                        changes_processed += 1

                    # Flush producer
                    producer.flush()

                    # Update tracking to the next LSN after the last change processed
                    # Use sys.fn_cdc_increment_lsn to get next LSN and avoid reprocessing
                    cursor = conn.cursor()
                    cursor.execute("SELECT sys.fn_cdc_increment_lsn(?)", (last_change_lsn,))
                    last_lsn = cursor.fetchone()[0]
                    cursor.close()

                    # Save state after successful batch
                    save_last_lsn(last_lsn)

                    logger.info(f"Published {len(changes)} change(s) (total: {changes_processed})")
                else:
                    logger.debug("No new changes")

                # Wait before next poll
                time.sleep(POLL_INTERVAL)

            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break

            except Exception as e:
                logger.error(f"Error processing changes: {e}", exc_info=True)
                time.sleep(POLL_INTERVAL)
                continue

    finally:
        logger.info("Shutting down")
        save_last_lsn(last_lsn)
        conn.close()
        logger.info(f"Processed {changes_processed} total changes")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)
