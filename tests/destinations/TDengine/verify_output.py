import taosrest
import os
import time

def main():
    host = "tdengine"
    port = 6041
    database = "test_db"
    min_expected_rows = int(os.getenv("TEST_MESSAGE_COUNT", "1"))

    print(f"Verifying data in TDengine at {host}:{port}")

    # Connect to TDengine with retries
    max_retries = 5
    retry_delay = 2
    conn = None

    for attempt in range(max_retries):
        try:
            conn = taosrest.connect(
                url=f"http://{host}:{port}",
                user="root",
                password="taosdata",
                timeout=30
            )
            print("Connected to TDengine successfully")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect to TDengine after {max_retries} attempts: {e}")
                exit(1)

    # Query data from the supertable with retries
    try:
        print("Querying data from sensor_data supertable...")

        rows = []
        max_query_attempts = 5
        for attempt in range(max_query_attempts):
            result = conn.query(f"SELECT * FROM {database}.sensor_data ORDER BY _ts")
            rows = list(result)
            print(f"Query attempt {attempt + 1}: Found {len(rows)} rows")

            if len(rows) >= min_expected_rows:
                break
            elif attempt < max_query_attempts - 1:
                print(f"Waiting for more data... (expected at least {min_expected_rows})")
                time.sleep(3)

        if len(rows) < min_expected_rows:
            print(f"FAILED: Expected at least {min_expected_rows} rows, got {len(rows)}")
            exit(1)

        rows_to_check = min(len(rows), 3)
        for i in range(rows_to_check):
            row = rows[i]
            print(f"Row {i}: {row}")
            # Row format: (timestamp, temperature, humidity, sensor_id)
            if len(row) < 4:
                print(f"FAILED: Row {i} has {len(row)} columns, expected 4")
                exit(1)

            # Check that temperature and humidity are present and numeric
            temperature = row[1]
            humidity = row[2]
            sensor_id = row[3]

            if temperature is None:
                print(f"FAILED: Row {i} has null temperature")
                exit(1)
            if humidity is None:
                print(f"FAILED: Row {i} has null humidity")
                exit(1)
            if sensor_id is None:
                print(f"FAILED: Row {i} has null sensor_id")
                exit(1)

        print(f"Success: Verified {len(rows)} rows in TDengine")

        result = conn.query(f"SELECT DISTINCT sensor_id FROM {database}.sensor_data")
        sensor_ids = [row[0] for row in list(result)]
        print(f"Found sensor IDs: {sensor_ids}")

        conn.close()
        exit(0)

    except Exception as e:
        print(f"Error querying data: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
