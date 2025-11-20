"""
Produce test data for Quix Lake Timeseries destination tests.

Generates test messages with timestamps and partitionable fields (location, sensor_type)
to verify Hive partitioning and time-based partitioning functionality.
"""
import os
import time
import json
from datetime import datetime, timezone
from quixstreams import Application


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_INPUT_TOPIC", "test-quixlake-input")
    message_count = int(os.getenv("TEST_MESSAGE_COUNT", "10"))

    print(f"Producing {message_count} test messages to topic: {topic_name}")

    app = Application(
        broker_address=broker_address,
        producer_extra_config={
            "allow.auto.create.topics": "true"
        }
    )

    topic = app.topic(topic_name)

    # Generate test data with multiple partitionable dimensions
    locations = ["NYC", "LA", "CHI"]
    sensor_types = ["temperature", "humidity", "pressure"]

    # Use a fixed timestamp for consistent testing (2024-01-15 12:00:00 UTC)
    base_timestamp_ms = int(datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)

    with app.get_producer() as producer:
        for i in range(message_count):
            # Distribute messages across different partitions
            location = locations[i % len(locations)]
            sensor_type = sensor_types[i % len(sensor_types)]

            # Add some time variation (each message is 1 hour apart)
            timestamp_ms = base_timestamp_ms + (i * 3600 * 1000)

            message = {
                "id": i,
                "location": location,
                "sensor_type": sensor_type,
                "value": round(20.0 + (i * 1.5), 2),  # Incrementing sensor value
                "ts_ms": timestamp_ms,
                "status": "active",
                "metadata": {
                    "device_id": f"device_{i % 3}",
                    "firmware": "v1.2.3"
                }
            }

            # Convert timestamp to human-readable for logging
            dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
            print(f"Producing message {i}: location={location}, sensor_type={sensor_type}, "
                  f"ts={dt.isoformat()}, value={message['value']}")

            serialized = json.dumps(message).encode('utf-8')

            producer.produce(
                topic=topic.name,
                key=f"key_{location}_{sensor_type}_{i}",
                value=serialized
            )

        producer.flush()

    print(f"\nSuccessfully produced {message_count} messages")
    print(f"Messages span from {datetime.fromtimestamp(base_timestamp_ms / 1000, tz=timezone.utc).isoformat()}")
    print(f"            to {datetime.fromtimestamp((base_timestamp_ms + (message_count - 1) * 3600 * 1000) / 1000, tz=timezone.utc).isoformat()}")
    print(f"Locations: {locations}")
    print(f"Sensor types: {sensor_types}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
