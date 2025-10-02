import os
import time
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    output_topic = os.getenv("TEST_OUTPUT_TOPIC", "test-s3-output")
    timeout = int(os.getenv("TEST_TIMEOUT", "60"))
    min_expected_messages = 1

    print(f"Consuming from output topic: {output_topic}")
    print(f"Waiting for at least {min_expected_messages} messages with timeout of {timeout}s")

    app = Application(
        broker_address=broker_address,
        consumer_group=f"test-consumer-{int(time.time())}",
        auto_offset_reset="earliest"
    )

    topic = app.topic(output_topic)
    list_sink = ListSink()

    sdf = app.dataframe(topic)
    sdf.sink(list_sink)

    app.run(timeout=timeout, count=10)

    message_count = len(list_sink)
    print(f"Received {message_count} messages from output topic")

    if message_count < min_expected_messages:
        print(f"FAILED: Expected at least {min_expected_messages} messages, got {message_count}")
        exit(1)

    # Verify first message structure
    first_message = list_sink[0]
    expected_fields = {"id", "name", "value"}
    actual_fields = set(first_message.keys())

    print(f"First message: {first_message}")
    print(f"Expected fields: {expected_fields}")
    print(f"Actual fields: {actual_fields}")

    if not expected_fields.issubset(actual_fields):
        print(f"FAILED: Missing fields. Expected: {expected_fields}, Got: {actual_fields}")
        exit(1)

    # Verify field types
    if not isinstance(first_message["id"], int):
        print(f"FAILED: 'id' should be integer, got {type(first_message['id'])}")
        exit(1)

    if not isinstance(first_message["name"], str):
        print(f"FAILED: 'name' should be string, got {type(first_message['name'])}")
        exit(1)

    if not isinstance(first_message["value"], int):
        print(f"FAILED: 'value' should be integer, got {type(first_message['value'])}")
        exit(1)

    print("Field types validated successfully")

    unique_ids = set(msg["id"] for msg in list_sink)
    print(f"Unique IDs found: {unique_ids}")

    if len(unique_ids) < 1:
        print(f"FAILED: Should have at least 1 unique ID, got {len(unique_ids)}")
        exit(1)

    print(f"SUCCESS: Verified {message_count} messages with correct structure and {len(unique_ids)} unique records")
    exit(0)


if __name__ == "__main__":
    main()
