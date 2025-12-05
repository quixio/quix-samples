import os
import json
from quixstreams import Application

def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_OUTPUT_TOPIC", "test-influxdb3-output")
    min_expected_messages = 5

    print(f"Consuming from topic: {topic_name}")

    app = Application(broker_address=broker_address, auto_offset_reset="earliest")

    topic = app.topic(topic_name)

    messages = []

    with app.get_consumer() as consumer:
        consumer.subscribe([topic_name])

        # Consume messages for a limited time
        for _ in range(50):  # Try up to 50 messages
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                break
            if msg.error():
                continue

            value = msg.value()
            if value:
                message = json.loads(value.decode('utf-8'))
                messages.append(message)

    print(f"Consumed {len(messages)} messages")

    if len(messages) < min_expected_messages:
        print(f"FAILED: Expected at least {min_expected_messages} messages, got {len(messages)}")
        exit(1)

    # Verify message structure
    for i, message in enumerate(messages[:3]):  # Check first 3 messages
        print(f"Message {i}: {message}")

        # Check required fields from InfluxDB data
        if 'sensor_id' not in message:
            print(f"FAILED: Message {i} missing 'sensor_id' tag")
            exit(1)
        if 'temperature' not in message:
            print(f"FAILED: Message {i} missing 'temperature' field")
            exit(1)
        if 'humidity' not in message:
            print(f"FAILED: Message {i} missing 'humidity' field")
            exit(1)
        if 'time' not in message:
            print(f"FAILED: Message {i} missing 'time' field")
            exit(1)

    print(f"Success: Verified {len(messages)} messages with correct structure from InfluxDB 3 source")
    exit(0)

if __name__ == "__main__":
    main()
