import taosrest
import os
import time

def main():
    host = "tdengine"
    port = 6041
    database = "test_db"

    # Wait for TDengine to be ready
    max_retries = 10
    for i in range(max_retries):
        try:
            print(f"Attempting to connect to TDengine at {host}:{port}... (attempt {i+1}/{max_retries})")
            conn = taosrest.connect(
                url=f"http://{host}:{port}",
                user="root",
                password="taosdata",
                timeout=30
            )
            print("Connected to TDengine successfully")
            break
        except Exception as e:
            print(f"Connection attempt {i+1} failed: {e}")
            if i < max_retries - 1:
                time.sleep(2)
            else:
                print("Max retries reached, exiting")
                exit(1)

    # Create database
    try:
        print(f"Creating database: {database}")
        conn.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        print(f"Database {database} created successfully")
    except Exception as e:
        print(f"Error creating database: {e}")
        exit(1)

    # Don't pre-create supertable - TDengine's InfluxDB API will auto-create it
    # from the line protocol data
    print("Skipping supertable creation - will be auto-created by InfluxDB API")

    conn.close()
    print("Setup complete")
    exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
