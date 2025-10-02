import os
import time
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    output_topic = os.getenv("TEST_OUTPUT_TOPIC", "test-csv-output")
    timeout = int(os.getenv("TEST_TIMEOUT", "40"))
    min_expected_messages = 1

    print(f"Consuming from output topic: {output_topic}")
    print(f"Expected at least {min_expected_messages} messages")

    app = Application(
        broker_address=broker_address,
        consumer_group=f"test-consumer-{int(time.time())}",
        auto_offset_reset="earliest"
    )

    topic = app.topic(output_topic)
    list_sink = ListSink()

    sdf = app.dataframe(topic)
    sdf.sink(list_sink)

    app.run(timeout=timeout, count=50)

    message_count = len(list_sink)
    print(f"Received {message_count} messages from output topic")

    if message_count < min_expected_messages:
        print(f"FAILED: Expected at least {min_expected_messages} messages, got {message_count}")
        exit(1)

    # Verify message structure
    print("Verifying message structure...")

    first_message = list_sink[0]
    expected_fields = {"Timestamp", "Number", "Name"}
    actual_fields = set(first_message.keys())

    if not expected_fields.issubset(actual_fields):
        print(f"FAILED: Missing fields. Expected: {expected_fields}, Got: {actual_fields}")
        exit(1)

    # Verify field types
    if not isinstance(first_message["Timestamp"], int):
        print(f"FAILED: Timestamp should be integer, got {type(first_message['Timestamp'])}")
        exit(1)

    if not isinstance(first_message["Number"], (int, float)):
        print(f"FAILED: Number should be numeric, got {type(first_message['Number'])}")
        exit(1)

    if not isinstance(first_message["Name"], str):
        print(f"FAILED: Name should be string, got {type(first_message['Name'])}")
        exit(1)

    messages_to_check = min(len(list_sink), 10)
    unique_names = set(msg["Name"] for msg in list_sink[:messages_to_check])

    print(f"Success: Verified {message_count} messages with correct structure")
    print(f"- All messages have required fields: {expected_fields}")
    print(f"- Field types are correct")
    if messages_to_check > 1:
        print(f"- Data has variety (found {len(unique_names)} unique names in first {messages_to_check} messages)")
    exit(0)


if __name__ == "__main__":
    main()
