#!/usr/bin/env python3
"""
Compact small Parquet files written by the DuckDB sink into larger
files (≈ 256 MB) per partition directory on S3.

Requirements
------------
pip install duckdb boto3

Safety
------
• Pass DRY_RUN=1 to do everything except DELETE the originals.
• A file-lock object is written to S3 so only one job runs per prefix.
"""

import os, re, sys, uuid, json, time, logging
from collections import defaultdict
from pathlib import PurePosixPath
from typing import List

import boto3
import duckdb

from dotenv import load_dotenv
load_dotenv(".env")

# ───────────────────────────────────────────────────────────────
# CONFIGURATION (env vars are easiest to tweak in prod)
# ───────────────────────────────────────────────────────────────
BUCKET          = os.environ["S3_BUCKET"]                 # "quix-test-bucket"
PREFIX          = os.getenv("S3_PREFIX", "events4")        # "events/"
SIZE_THRESHOLD  = int(os.getenv("SMALL_FILE_MB", 64))     # < 64 MB ⇒ 'small'
TARGET_MB       = int(os.getenv("TARGET_FILE_MB", 256))   # write ≈ 256 MB
DRY_RUN         = os.getenv("DRY_RUN", "0") == "1"        # no delete if 1
LOCK_KEY        = f"{PREFIX.rstrip('/')}/_compaction.lock"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s  %(message)s")
log = logging.getLogger("compact-job")

# ───────────────────────────────────────────────────────────────
# S3 helpers
# ───────────────────────────────────────────────────────────────
s3   = boto3.resource("s3")
bucket = s3.Bucket(BUCKET)

#def acquire_lock():
#    """Write a 0-byte object; fail if it already exists."""
    #if any(o.key == LOCK_KEY for o in bucket.objects.filter(Prefix=LOCK_KEY)):
        #log.error("Lockfile %s already present – another compaction running", LOCK_KEY)
        #sys.exit(1)
    #bucket.put_object(Key=LOCK_KEY, Body=b"")
    #log.info("Lock acquired")

#def release_lock():
    #bucket.Object(LOCK_KEY).delete()
    #log.info("Lock released")

def list_parquet_objects() -> List[dict]:
    objs = []
    for obj in bucket.objects.filter(Prefix=PREFIX):
        print(obj.key)
        if obj.key.endswith(".parquet"):
            objs.append({"key": obj.key, "size": obj.size})
    return objs


def s3_key(uri: str) -> str:
    """Convert full s3://… URI → bucket-relative key."""
    return uri.split("/", 3)[3]          # keep the part after the bucket

def delete_keys(keys: list[str]):
    CHUNK = 1000                         # DeleteObjects max
    for i in range(0, len(keys), CHUNK):
        batch = [{"Key": s3_key(k)} for k in keys[i:i+CHUNK]]
        resp  = bucket.delete_objects(Delete={"Objects": batch, "Quiet": True})
        for err in resp.get("Errors", []):
            log.error("❌ could not delete %s – %s", err["Key"], err["Message"])
# ───────────────────────────────────────────────────────────────
# Partition discovery – split on "key=value/" pattern
# ───────────────────────────────────────────────────────────────
PARTITION_RE = re.compile(r"[a-zA-Z0-9_]+=([^/]+)/")

def partition_path(key: str) -> str:
    p = PurePosixPath(key)
    # everything up to but not including file name
    return str(p.parent)

# ───────────────────────────────────────────────────────────────
# DuckDB – one connection reused for all compactions
# ───────────────────────────────────────────────────────────────
con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs")
con.execute(f"SET s3_region='{os.environ['AWS_REGION']}'")

def compact_files(part_dir: str, files: List[str]):
    """Merge <files> (all small) into one ~TARGET_MB Parquet."""
    log.info("⛓  compacting %d files under %s", len(files), part_dir)

    files_quoted = "', '".join(files)
    tmp_view     = f"src_{uuid.uuid4().hex[:8]}"

    # create a DuckDB view over the small files
    con.execute(f"""
        CREATE VIEW {tmp_view} AS
        SELECT * FROM read_parquet(
            ['{files_quoted}'],
            union_by_name = TRUE
        );
    """)

    # write one new Parquet file
    target = f"s3://{BUCKET}/{part_dir}/compact_{uuid.uuid4().hex}.parquet"
    con.execute(f"""
        COPY {tmp_view}
        TO '{target}'
        (FORMAT PARQUET);
    """)
    con.execute(f"DROP VIEW {tmp_view}")
    log.info("🆗  wrote %s", target)

    # delete originals
    if not DRY_RUN:
        delete_keys(files)
        log.info("🗑️   deleted %d small files", len(files))

# ───────────────────────────────────────────────────────────────
# MAIN
# ───────────────────────────────────────────────────────────────
def main():
    #acquire_lock()
    #try:
    small_by_partition = defaultdict(list)

    start_time = time.time()
    log.info("Getting all parquet files...")
    s3_files = list_parquet_objects()
    log.info(f"{len(s3_files)} file names loaded in {time.time() - start_time}s")

    for obj in s3_files:
        if obj["size"] < SIZE_THRESHOLD * 1024 * 1024:
            part = partition_path(obj["key"])
            small_by_partition[part].append("s3://quix-test-bucket/" + obj["key"])

    if not small_by_partition:
        log.info("No small files found – nothing to compact.")
        return

    for part, files in small_by_partition.items():
        compact_files(part, files)

    log.info("Compaction finished.")
    #finally:
        #release_lock()

if __name__ == "__main__":
    main()