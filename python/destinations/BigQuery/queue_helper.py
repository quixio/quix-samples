import time
from queue import Queue
import threading
from setup_logger import logger
from bigquery_helper import create_column, Null, insert_row

run = True

def stop():
    global run
    run = False

def consume_queue(conn, table_name: str, insert_queue: Queue, wait_interval: float, batch_size: int):
    batch = []
    while run:

        if insert_queue.empty() and len(batch) == 0:
            time.sleep(wait_interval)
            continue

        tid = threading.get_ident()

        if not insert_queue.empty() and len(batch) < batch_size:
            row = insert_queue.get()
            batch.append(row)

        else:
            # Get all column names
            all_cols = list(set().union(*batch))

            # Create Columns if not exist
            for col in all_cols:
                if col[:4] == 'TAG_':
                    try:
                        create_column(conn, table_name, col, 'STRING')
                    except Exception as error:
                        logger.error(error)
                        continue
                if col[-2:] == '_s':
                    try:
                        create_column(conn, table_name, col, 'STRING')
                    except Exception as error:
                        logger.error(error)
                        continue
                if col[-2:] == '_n':
                    try:
                        create_column(conn, table_name, col, 'NUMERIC')
                    except Exception as error:
                        logger.error(error)
                        continue

            all_rows = []
            for r in batch:
                r_v = []
                for col in all_cols:
                    r_v.append(r.get(col, Null()))
                all_rows.append(r_v)
            logger.debug(
                f"Inserting row from thread: {tid}, queue size: {insert_queue.qsize()}")
            try:
                insert_row(conn, table_name, all_cols, all_rows)

            except Exception as error:
                logger.error(error)
                continue
            for i in range(len(batch)):
                insert_queue.task_done()
            batch = [] #Empty batch