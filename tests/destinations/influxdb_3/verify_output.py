import os
from influxdb_client import InfluxDBClient

def main():
    # InfluxDB connection details
    host = "http://influxdb:8086"
    token = "testtokenabc123"
    org = "testorg"
    bucket = "testdb"
    measurement = "test_measurement"
    expected_count = 1

    print(f"Connecting to InfluxDB at {host}")

    # Connect to InfluxDB 2.x
    client = InfluxDBClient(url=host, token=token, org=org)
    query_api = client.query_api()

    # Query data using Flux
    query = f'''
    from(bucket: "{bucket}")
        |> range(start: -1m)
        |> filter(fn: (r) => r._measurement == "{measurement}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    print(f"Querying: {query}")
    result = query_api.query(query, org=org)

    # Get points from result
    points = []
    for table in result:
        for record in table.records:
            points.append(record.values)

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
