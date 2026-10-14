#!/usr/bin/env python3
"""
Perform database operations to test CDC.

Performs INSERT, UPDATE, and DELETE operations that should be captured by CDC.
"""
import pymssql
import os
import time

# Connection parameters
host = os.environ['SQL_HOST']
port = int(os.environ.get('SQL_PORT', 1433))
user = os.environ['SQL_USER']
password = os.environ['SQL_PASSWORD']
database = os.environ['SQL_DATABASE']
schema = os.environ.get('SQL_SCHEMA', 'dbo')
table = os.environ['SQL_TABLE']

print(f"Connecting to SQL Server database '{database}'...")
conn = pymssql.connect(
    server=host,
    port=port,
    user=user,
    password=password,
    database=database,
    charset='UTF-8',
    as_dict=False
)

cursor = conn.cursor()

print("Performing CDC-trackable operations...")

# INSERT operations
print("1. Inserting 3 records...")
test_records = [
    ('test1', 100),
    ('test2', 200),
    ('test3', 300),
]

inserted_ids = []
for name, value in test_records:
    cursor.execute(
        f"INSERT INTO {schema}.{table} (name, value) VALUES (%s, %s); SELECT SCOPE_IDENTITY()",
        (name, value)
    )
    inserted_id = cursor.fetchone()[0]
    inserted_ids.append(int(inserted_id))
    print(f"   Inserted: id={inserted_id}, name={name}, value={value}")
    time.sleep(0.1)

conn.commit()

# Wait for CDC to capture inserts
time.sleep(1)

# UPDATE operation
print(f"2. Updating record id={inserted_ids[0]}...")
cursor.execute(
    f"UPDATE {schema}.{table} SET value = 150 WHERE id = %s",
    (inserted_ids[0],)
)
conn.commit()
print(f"   Updated: id={inserted_ids[0]}, value=150")

# Wait for CDC to capture update
time.sleep(1)

# DELETE operation
print(f"3. Deleting record id={inserted_ids[2]}...")
cursor.execute(
    f"DELETE FROM {schema}.{table} WHERE id = %s",
    (inserted_ids[2],)
)
conn.commit()
print(f"   Deleted: id={inserted_ids[2]}")

# Wait for CDC to capture delete
time.sleep(1)

print(f"\nSummary:")
print(f"  - Inserted 3 records (ids: {inserted_ids})")
print(f"  - Updated 1 record (id: {inserted_ids[0]})")
print(f"  - Deleted 1 record (id: {inserted_ids[2]})")
print(f"  - Expected CDC events: 5 (3 inserts + 1 update + 1 delete)")

cursor.close()
conn.close()

print("Data modification complete")
