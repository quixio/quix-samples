import os
from influxdb import InfluxDBClient

def main():
    # InfluxDB connection details
    host = "influxdb"
    port = 8086
    username = "testuser"
    password = "testpass"
    database = "testdb"
    measurement = "test_measurement"
    expected_count = 1

    print(f"Connecting to InfluxDB at {host}:{port}")

    # Connect to InfluxDB
    client = InfluxDBClient(
        host=host,
        port=port,
        username=username,
        password=password,
        database=database
    )

    # Query data
    query = f'SELECT * FROM "{measurement}"'
    print(f"Querying: {query}")
    result = client.query(query)

    # Get points from result
    points = list(result.get_points())
    actual_count = len(points)

    print(f"Found {actual_count} points in InfluxDB measurement '{measurement}'")

    if actual_count < expected_count:
        print(f"FAILED: Expected at least {expected_count} points, got {actual_count}")
        exit(1)

    # Verify point structure
    for i, point in enumerate(points[:3]):  # Check first 3 points
        print(f"Point {i}: sensor_id={point.get('sensor_id')}, temperature={point.get('temperature')}, humidity={point.get('humidity')}")

        # Check required fields
        if 'sensor_id' not in point:
            print(f"FAILED: Point {i} missing 'sensor_id' tag")
            exit(1)
        if 'temperature' not in point:
            print(f"FAILED: Point {i} missing 'temperature' field")
            exit(1)
        if 'humidity' not in point:
            print(f"FAILED: Point {i} missing 'humidity' field")
            exit(1)

    print(f"Success: Verified {actual_count} points with correct structure in InfluxDB")
    client.close()
    exit(0)

if __name__ == "__main__":
    main()
