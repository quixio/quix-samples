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
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["POSTGRES_DB"]
    )
    conn.autocommit = True
    cursor = conn.cursor()

    schema = os.environ["POSTGRES_SCHEMA"]
    table = os.environ["POSTGRES_TABLE"]

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
