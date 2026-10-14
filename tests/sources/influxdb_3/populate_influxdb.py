import os
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

def main():
    # InfluxDB connection details
    url = os.getenv("INFLUXDB_HOST", "http://influxdb:8086")
    token = os.getenv("INFLUXDB_TOKEN", "testtokenabc123")
    org = os.getenv("INFLUXDB_ORG", "testorg")
    bucket = os.getenv("INFLUXDB_DATABASE", "testdb")
    measurement = os.getenv("INFLUXDB_MEASUREMENT_NAME", "sensor_data")

    print(f"Connecting to InfluxDB at {url}")

    # Create client
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Write test data points with current timestamps
    points = []
    base_time = datetime.utcnow()

    for i in range(5):
        point = Point(measurement) \
            .tag("sensor_id", f"sensor_{i % 2}") \
            .tag("location", "test_lab") \
            .field("temperature", 20.0 + i) \
            .field("humidity", 50.0 + i * 2) \
            .time(base_time + timedelta(milliseconds=i * 100))
        points.append(point)
        print(f"Writing point {i}: sensor_id=sensor_{i % 2}, temperature={20.0 + i}, humidity={50.0 + i * 2}")

    # Write all points
    write_api.write(bucket=bucket, org=org, record=points)

    print(f"Successfully wrote {len(points)} points to InfluxDB measurement '{measurement}'")

    client.close()
    exit(0)

if __name__ == "__main__":
    main()
