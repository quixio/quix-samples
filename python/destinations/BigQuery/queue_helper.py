import time
from queue import Queue
import threading

from bigquery_helper import create_column, Null, insert_row

def insert_from_queue(conn, table_name: str, insert_queue: Queue, wait_interval: float, batch_size: int):
    batch = []
    while True:

        if insert_queue.empty():
            time.sleep(wait_interval)
            continue

        tid = threading.get_ident()
        if len(batch) < batch_size:
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
                        print(error)
                        continue
                if col[-2:] == '_s':
                    try:
                        create_column(conn, table_name, col, 'STRING')
                    except Exception as error:
                        print(error)
                        continue
                if col[-2:] == '_n':
                    try:
                        create_column(conn, table_name, col, 'NUMERIC')
                    except Exception as error:
                        print(error)
                        continue

            all_rows = []
            for r in batch:
                r_v = []
                for col in all_cols:
                    r_v.append(r.get(col, Null()))
                all_rows.append(r_v)
            print(
                f"Inserting row from thread: {tid}, queue size: {insert_queue.qsize()}")
            try:
                insert_row(conn, table_name, all_cols, all_rows)
            except Exception as error:
                print(error)
                continue
            batch = [] #Empty batch
