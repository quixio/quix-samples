#!/usr/bin/env python3
"""
Script to perform INSERT, UPDATE, and DELETE operations on the test table.
These operations should be captured by the CDC source and published to Kafka.
"""
import psycopg2
import os
import sys
import time

def main():
    # Connect to Postgres
    conn = psycopg2.connect(
        host=os.environ["PG_HOST"],
        port=os.environ["PG_PORT"],
        user=os.environ["PG_USER"],
        password=os.environ["PG_PASSWORD"],
        database=os.environ["PG_DATABASE"]
    )
    conn.autocommit = True
    cursor = conn.cursor()

    schema = os.environ["PG_SCHEMA"]
    table = os.environ["PG_TABLE"]
    table_name = f"{schema}.{table}"

    try:
        # INSERT operation
        print("Performing INSERT operation...")
        cursor.execute(f"""
            INSERT INTO {table_name} (name, value)
            VALUES ('test_record_1', 100)
        """)
        time.sleep(0.5)

        # UPDATE operation
        print("Performing UPDATE operation...")
        cursor.execute(f"""
            UPDATE {table_name}
            SET value = 200
            WHERE name = 'test_record_1'
        """)
        time.sleep(0.5)

        # DELETE operation
        print("Performing DELETE operation...")
        cursor.execute(f"""
            DELETE FROM {table_name}
            WHERE name = 'test_record_1'
        """)
        time.sleep(0.5)

        print(f"Completed 3 operations (INSERT, UPDATE, DELETE) on {table_name}")

    except Exception as e:
        print(f"Error performing database operations: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
