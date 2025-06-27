from quixstreams.sinks import BatchingSink, SinkBatch
import pyarrow as pa
import pyarrow.compute as pc
import os
import time
import time
import os, time
import time
import pyarrow as pa
import pyarrow.compute as pc
import datetime
from typing import List, Dict, Any
import logging
    
import duckdb

class DuckDbSink(BatchingSink):
    
    """
    Writes Kafka batches directly to DuckDB + Hive-style Parquet.
    """
    def __init__(self, 
                 s3_bucket: str, 
                 s3_prefix: str, 
                 partition_keys: List[str],
                 guid_pattern: str = "data_{uuidv4}.parquet"):
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.s3_root   = f"s3://{s3_bucket}/{s3_prefix}/"
        self.table_name = s3_prefix
        self.partition_keys = partition_keys
        self.guid_pattern = guid_pattern

        self.logger = logging.getLogger(__name__)

        super().__init__()
        

    # BatchingSink hook
    def setup(self):
        self.con  = duckdb.connect()
        
        # 1. enable the S3 extension
        self.con.execute("INSTALL httpfs; LOAD httpfs")
        
        # 2. (optional) set options explicitly so you see typos immediately
        self.con.execute("SET s3_region='eu-west-2'")
        self.con.execute("SET s3_access_key_id=$1", [os.environ["AWS_ACCESS_KEY_ID"]])
        self.con.execute("SET s3_secret_access_key=$1", [os.environ["AWS_SECRET_ACCESS_KEY"]])

        # base table – minimal columns, grow on demand
        self.con.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                ts_ms       BIGINT,
                day         DATE
            );
        """)


        for name, typ, *_ in self.con.execute(f"PRAGMA table_info('{self.table_name}')").fetchall():
            print(f"→ column `{name}` : {typ}")

  

    def _append_batch(self, batch: SinkBatch):
        
        for item in batch:
            item.value["ts_ms"] = item.timestamp
            item.value["__key"] = item.key  
            
        rows = [item.value for item in batch]

        self.ensure_columns(self.con, rows)
        table = pa.Table.from_pylist(rows)

        # 2) Add 'day' if needed, as before
        if 'day' in self.partition_keys and 'day' not in table.column_names:
            ts_ts = pc.cast(table['ts_ms'], pa.timestamp('ms'))
            day_col = pc.cast(ts_ts, pa.date32())
            table = table.append_column('day', day_col)

        # 3) Register as tmp_batch
        self.con.register('tmp_batch', table)

        # 4) Explicit‐column INSERT in the exact order of your DuckDB schema
        #    First, fetch DuckDB's column‐order so we never mistype:
        schema_info = self.con.execute(f"PRAGMA table_info('{self.table_name}')").fetchall()
        #  schema_info is a list of rows like [(0,'ts_ms','BIGINT',...), (1,'day','DATE',...), …]
        ordered_cols = [ row[1] for row in schema_info ]
        #  ordered_cols == ['ts_ms','day','usage_user','usage_system','usage_idle','hostname','timestamp']

        col_list_sql = ", ".join(ordered_cols)
        select_list_sql = ", ".join(f"{col}" for col in ordered_cols)

        # Now run the positional INSERT with matching column order
        self.con.execute(f"""
            INSERT INTO {self.table_name} ({col_list_sql})
            SELECT {select_list_sql}
            FROM tmp_batch;
        """)
        self.logger.info("Inserted %d rows into %s", len(rows), self.table_name)

        # 5) Unregister and write Parquet
        self.con.unregister('tmp_batch')
        self.write_parquet(self.con, rows)

    # BatchingSink required
    def write(self, batch: SinkBatch):
        attempts = 3
        while attempts:
            start = time.perf_counter()
            try:
                self._append_batch(batch)
                elapsed_ms = (time.perf_counter() - start) * 1000
                self.logger.info("✔ wrote %d rows in %.1f ms", len(batch), elapsed_ms)
                return
            except Exception as exc:
                attempts -= 1
                if attempts == 0:
                    raise
                self.logger.warning("Write failed (%s) – retrying …", exc)
                time.sleep(3)
            # back-pressure not needed; local writes rarely block

    def write_parquet(self, con: duckdb.DuckDBPyConnection,
                       rows: list[dict]):
        if not rows:
            return

        # 1. Build a PyArrow Table from the list-of-dicts
        #    and derive "day" inside Arrow so COPY sees it as a column.
        table = pa.Table.from_pylist(rows)

        # If "day" isn't already in your rows, add it as a DATE column:
        if 'day' not in table.column_names:
            # compute ts_ms / 1000 → timestamp[s], then cast to date32
            ts_col = pc.divide(table['ts_ms'], 1000).cast(pa.timestamp('s'))
            day_col = pc.cast(ts_col, pa.date32())
            table = table.append_column('day', day_col)

        # 2. Register the Arrow Table as a DuckDB view (zero-copy).
        con.register('tmp_batch', table)

        part_sql = ", ".join(self.partition_keys)  # e.g. "day, hostname"

        # 4. COPY that view to S3 (or local) in one shot.
        con.execute(f"""
            COPY tmp_batch
            TO '{self.s3_root}{self.guid_pattern}'
            (FORMAT PARQUET,
            FILENAME_PATTERN '{self.guid_pattern}',
            PARTITION_BY ({part_sql}),
            OVERWRITE_OR_IGNORE TRUE
            );
        """)
        con.unregister('tmp_batch')


    def python_type_to_sql(self, value: Any) -> str:
        """
        Infer a DuckDB/SQL type from a single Python value.
        """
        if value is None:
            return "VARCHAR"
        if isinstance(value, bool):
            return "BOOLEAN"
        if isinstance(value, int):
            return "BIGINT"
        if isinstance(value, float):
            return "DOUBLE"
        if isinstance(value, datetime.datetime):
            # full precision timestamp
            return "TIMESTAMP"
        if isinstance(value, datetime.date):
            # calendar date only (no time component)
            return "DATE"
        # fall back to string
        return "VARCHAR"


    def ensure_columns(self, con: duckdb.DuckDBPyConnection, rows: List[Dict[str, Any]]):
        cur_cols = {r[1]: r[2].upper()
                    for r in con.execute(f"PRAGMA table_info('{self.table_name}')").fetchall()}
        for row in rows:
            for col, val in row.items():
                want = None   # declared or None
                have = cur_cols.get(col)
                if have:
                    if want and have != want:
                        raise TypeError(f"Column {col} is {have}, env wants {want}")
                    continue
                sql_t = want or self.python_type_to_sql(val)
                con.execute(f"ALTER TABLE {self.table_name} ADD COLUMN {col} {sql_t}")
                cur_cols[col] = sql_t

