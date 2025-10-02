#!/usr/bin/env python3
"""
Setup SQL Server for CDC testing.

Creates database, table, and enables CDC.
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

print(f"Connecting to SQL Server at {host}:{port}")

# Connect to SQL Server (without specifying database to create it first)
conn = pymssql.connect(
    server=host,
    port=port,
    user=user,
    password=password,
    charset='UTF-8',
    as_dict=False,
    autocommit=True  # Required for CREATE DATABASE
)

cursor = conn.cursor()

# Create database if it doesn't exist
print(f"Ensuring database '{database}' exists...")
cursor.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{database}') CREATE DATABASE {database}")
print(f"Database '{database}' ready")

cursor.close()
conn.close()

# Reconnect to the new database
print(f"Connecting to database '{database}'...")
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

# Create table if it doesn't exist
print(f"Ensuring table '{schema}.{table}' exists...")
cursor.execute(f"""
IF NOT EXISTS (SELECT * FROM sys.tables t
               JOIN sys.schemas s ON t.schema_id = s.schema_id
               WHERE s.name = '{schema}' AND t.name = '{table}')
BEGIN
    CREATE TABLE {schema}.{table} (
        id INT PRIMARY KEY IDENTITY(1,1),
        name NVARCHAR(100) NOT NULL,
        value INT NOT NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    )
END
ELSE
BEGIN
    -- Clear the table for clean test state
    TRUNCATE TABLE {schema}.{table}
END
""")
conn.commit()
print(f"Table '{schema}.{table}' ready")

# Enable CDC on database if not already enabled
print(f"Enabling CDC on database '{database}'...")
cursor.execute(f"IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = '{database}' AND is_cdc_enabled = 1) EXEC sys.sp_cdc_enable_db")
conn.commit()
print("CDC enabled on database")

# Wait a moment for CDC to initialize
time.sleep(2)

# Enable CDC on table if not already enabled
print(f"Enabling CDC on table '{schema}.{table}'...")
cursor.execute(f"""
IF NOT EXISTS (SELECT 1 FROM sys.tables t
               JOIN sys.schemas s ON t.schema_id = s.schema_id
               WHERE s.name = '{schema}' AND t.name = '{table}' AND t.is_tracked_by_cdc = 1)
BEGIN
    EXEC sys.sp_cdc_enable_table
        @source_schema = '{schema}',
        @source_name = '{table}',
        @role_name = NULL,
        @supports_net_changes = 1
END
""")
conn.commit()
print(f"CDC enabled on table '{schema}.{table}'")

# Verify CDC is enabled
cursor.execute(f"""
    SELECT is_tracked_by_cdc
    FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = '{schema}' AND t.name = '{table}'
""")
is_cdc_enabled = cursor.fetchone()[0]

if is_cdc_enabled:
    print(f"✓ CDC verification successful")
else:
    print(f"✗ CDC verification failed")
    exit(1)

cursor.close()
conn.close()

print("SQL Server setup complete")
