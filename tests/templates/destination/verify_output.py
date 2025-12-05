"""
Test verifier for [APP_NAME] destination output.

This script:
1. Connects to [DESTINATION_SYSTEM]
2. Queries/reads data that was written by the destination
3. Validates data count and structure
4. Exits with code 0 on success, 1 on failure

TODO: Replace all [PLACEHOLDERS] with your actual values
TODO: Install required client library if needed (e.g., pip install [client-library])
TODO: Customize connection and query logic for your destination system
"""
import os
# TODO: Import client library for your destination system
# EXAMPLE for InfluxDB: from influxdb_client import InfluxDBClient
# EXAMPLE for PostgreSQL: import psycopg2
# EXAMPLE for MongoDB: from pymongo import MongoClient
# EXAMPLE for Elasticsearch: from elasticsearch import Elasticsearch
# EXAMPLE for Redis: import redis


def main():
    # ===== CONNECTION CONFIGURATION =====
    # TODO: Replace with your destination system's connection parameters
    host = os.getenv("[DESTINATION_HOST_ENV]", "http://[destination-service]:[port]")
    # EXAMPLE: host = os.getenv("DB_HOST", "http://postgres:5432")
    # EXAMPLE: host = os.getenv("INFLUX_URL", "http://influxdb:8086")

    # TODO: Add authentication credentials (use test values, not production secrets)
    username = "[test-username]"  # EXAMPLE: "testuser"
    password = "[test-password]"  # EXAMPLE: "testpass123"
    token = "[test-token]"  # EXAMPLE: "testtokenabc123" (for token-based auth)

    # TODO: Add database/bucket/index/collection name
    database = "[test-database-name]"  # EXAMPLE: "testdb"
    collection = "[test-collection-name]"  # EXAMPLE: "measurements"

    # Test expectations
    expected_count = int(os.getenv("TEST_MESSAGE_COUNT", "5"))

    print(f"Connecting to [DESTINATION_SYSTEM] at {host}")

    # ===== CONNECT TO DESTINATION SYSTEM =====
    # TODO: Replace with actual connection code for your destination
    # EXAMPLE for InfluxDB 2.x:
    # client = InfluxDBClient(url=host, token=token, org=org)
    # query_api = client.query_api()

    # EXAMPLE for PostgreSQL:
    # conn = psycopg2.connect(host=host, database=database, user=username, password=password)
    # cursor = conn.cursor()

    # EXAMPLE for MongoDB:
    # client = MongoClient(host, username=username, password=password)
    # db = client[database]
    # collection = db[collection]

    # EXAMPLE for Elasticsearch:
    # client = Elasticsearch([host], basic_auth=(username, password))

    # ===== QUERY/READ DATA =====
    # TODO: Replace with actual query for your destination system
    # query = "[YOUR_QUERY]"  # EXAMPLE: "SELECT * FROM measurements"
    # print(f"Querying: {query}")

    # TODO: Execute query and get results
    # results = [execute_query_here]

    # EXAMPLE for SQL database:
    # cursor.execute("SELECT * FROM measurements ORDER BY timestamp")
    # rows = cursor.fetchall()
    # actual_count = len(rows)

    # EXAMPLE for InfluxDB:
    # query = f'from(bucket: "{bucket}") |> range(start: -1m) |> filter(fn: (r) => r._measurement == "{measurement}")'
    # result = query_api.query(query, org=org)
    # points = [record.values for table in result for record in table.records]
    # actual_count = len(points)

    # EXAMPLE for MongoDB:
    # documents = list(collection.find({}))
    # actual_count = len(documents)

    # EXAMPLE for Elasticsearch:
    # result = client.search(index=index_name, body={"query": {"match_all": {}}})
    # hits = result['hits']['hits']
    # actual_count = len(hits)

    # TODO: Replace with your actual count variable
    actual_count = 0  # PLACEHOLDER: Replace with actual count from query

    print(f"Found {actual_count} records in [DESTINATION_SYSTEM]")

    # ===== VALIDATE COUNT =====
    if actual_count < expected_count:
        print(f"FAILED: Expected at least {expected_count} records, got {actual_count}")
        exit(1)

    # ===== VALIDATE DATA STRUCTURE AND CONTENT =====
    # TODO: Iterate through results and validate each record
    # for i, record in enumerate(results[:3]):  # Check first 3 records as sample
    #     print(f"Record {i}: {record}")

    # TODO: Check required fields exist
    # PATTERN for dict-like results:
    # if '[field1_name]' not in record:
    #     print(f"FAILED: Record {i} missing '[field1_name]' field")
    #     exit(1)

    # TODO: Validate field values
    # PATTERN for value validation:
    # if record['[field1_name]'] not in ['expected_value1', 'expected_value2']:
    #     print(f"FAILED: Record {i} has invalid [field1_name]: {record['[field1_name]']}")
    #     exit(1)

    # TODO: Validate data types
    # PATTERN for type validation:
    # if not isinstance(record['[field2_name]'], float):
    #     print(f"FAILED: Record {i} [field2_name] is not a float: {type(record['[field2_name]'])}")
    #     exit(1)

    # EXAMPLE validation for InfluxDB:
    # for i, point in enumerate(points[:3]):
    #     if 'sensor_id' not in point:
    #         print(f"FAILED: Point {i} missing 'sensor_id' tag")
    #         exit(1)
    #     if 'temperature' not in point:
    #         print(f"FAILED: Point {i} missing 'temperature' field")
    #         exit(1)

    # EXAMPLE validation for SQL database:
    # for i, row in enumerate(rows[:3]):
    #     sensor_id, temperature, humidity, timestamp = row
    #     if not sensor_id.startswith('sensor_'):
    #         print(f"FAILED: Row {i} has invalid sensor_id: {sensor_id}")
    #         exit(1)

    print(f"Success: Verified {actual_count} records with correct structure in [DESTINATION_SYSTEM]")

    # ===== CLEANUP =====
    # TODO: Close connections
    # client.close()  # or conn.close(), etc.

    exit(0)

if __name__ == "__main__":
    main()
