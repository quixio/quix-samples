#!/usr/bin/env python3
"""
Setup script to create the database schema and table for Postgres CDC testing.
"""
import psycopg2
import os
import sys

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

    try:
        # Create schema if it doesn't exist
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        print(f"Schema '{schema}' created or already exists")

        # Create test table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema}.{table} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                value INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print(f"Table '{schema}.{table}' created or already exists")

        print("Database setup complete!")

    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
