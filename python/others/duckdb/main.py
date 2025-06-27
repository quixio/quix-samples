from flask import Flask, request, jsonify
from flask_cors import CORS
import duckdb
import boto3

# ────────────────────────────────
# config
# ────────────────────────────────
TABLE_NAME         = "events"                     # internal table
GUID_PATTERN       = "data_{uuidv4}"    # no name collisions
READ_PATTERN       = "data_*.parquet"    # no name collisions
PARTITION_KEYS     = ["day", "hostname"]       # basic keys

import os

from dotenv import load_dotenv
load_dotenv("duckdb/.env")


app          = Flask(__name__)
CORS(app)  # Enable CORS for all routes
con          = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs")

# Create state directory if it doesn't exist
os.makedirs("/app/state", exist_ok=True)
con = duckdb.connect(database="/app/state/duckdb.db", read_only=False)
        
# 1. enable the S3 extension
con.execute("INSTALL httpfs; LOAD httpfs")
        
        # 2. (optional) set options explicitly so you see typos immediately
con.execute("SET s3_region='eu-west-2'")
con.execute("SET s3_access_key_id=$1", [os.environ["AWS_ACCESS_KEY_ID"]])
con.execute("SET s3_secret_access_key=$1", [os.environ["AWS_SECRET_ACCESS_KEY"]])

# initialise (creates the metadata DB + directory)
con.execute("SET memory_limit = '4GB';")
# Create temp directory if it doesn't exist
os.makedirs("/app/state/duckdb_swap", exist_ok=True)
con.execute("SET temp_directory = '/app/state/duckdb_swap';")
con.execute("SET max_temp_directory_size = '100GB';")

# S3 performance optimizations
con.execute("SET threads=32;")
con.execute("SET enable_object_cache=true;")
con.execute("SET s3_use_ssl=true;")


# ────────────────────────────────
# /query  (raw SQL text)
# ────────────────────────────────
@app.route("/query", methods=["POST"])
def query():

    raw_sql = request.get_data(as_text=True)
    if not raw_sql.strip().lower().startswith("select"):
        return jsonify({"error": "only SELECT allowed"}), 400
    try:
         # 1) run plain EXPLAIN (text)
        rows = con.execute(f"EXPLAIN ANALYZE {raw_sql}").fetchall()
        #rows is a list of single‐element tuples, e.g. [("└─ Scan …",), ("   └─ …",), …]
        plan_text = rows[0][1].split("\n")
        print("\n── DuckDB EXPLAIN ──────────────────────────────────")
        for line in plan_text:
            print(line)
        print("────────────────────────────────────────────────────\n")
        
        result = con.execute(raw_sql).fetch_df()
        return str(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ────────────────────────────────
# /hive-folders  (list all hive folders tree)
# ────────────────────────────────
@app.route("/hive-folders", methods=["GET"])
def hive_folders():
    try:
        # Use boto3 to list folders in S3 bucket
        s3_client = boto3.client('s3',
                                aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                                aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                                region_name='eu-west-2')
        
        # Get parent folder parameter for lazy loading
        parent_folder = request.args.get('parent', '')
        
        s3_prefix = os.environ.get("S3_PREFIX", "events4")
        # Ensure prefix ends with / to list contents inside the folder
        if not s3_prefix.endswith('/'):
            s3_prefix += '/'
        
        # Add parent folder to prefix if provided
        if parent_folder:
            s3_prefix += parent_folder
            if not s3_prefix.endswith('/'):
                s3_prefix += '/'
        
        print(f"Using S3 prefix: {s3_prefix}")
        
        # List folders with delimiter to get immediate children only
        paginator = s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket='quix-test-bucket', Prefix=s3_prefix, Delimiter='/')
        
        folders = []
        
        for page in page_iterator:
            # Get common prefixes (folders)
            if 'CommonPrefixes' in page:
                for prefix in page['CommonPrefixes']:
                    folder_path = prefix['Prefix'].replace(s3_prefix, '').rstrip('/')
                    if folder_path:
                        folders.append(folder_path)
        
        print(f"Folders found: {folders}")
        
        return jsonify({"folders": folders, "parent": parent_folder})
    except Exception as e:
        print(f"Error in hive_folders: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)