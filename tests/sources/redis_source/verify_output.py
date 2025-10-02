import os
import time
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    output_topic = os.getenv("TEST_OUTPUT_TOPIC", "test-redis-output")
    timeout = int(os.getenv("TEST_TIMEOUT", "40"))
    min_expected_messages = 1

    print(f"Consuming from output topic: {output_topic}")
    print(f"Waiting for messages (timeout: {timeout}s, min expected: {min_expected_messages})...")

    # Wait a bit for source to start producing
    time.sleep(3)

    app = Application(
        broker_address=broker_address,
        consumer_group=f"test-consumer-{int(time.time())}",
        auto_offset_reset="earliest"
    )

    topic = app.topic(output_topic, value_deserializer="bytes")
    list_sink = ListSink()

    sdf = app.dataframe(topic)
    sdf.sink(list_sink)

    app.run(timeout=timeout, count=10)

    message_count = len(list_sink)
    print(f"Received {message_count} messages from output topic")

    if message_count < min_expected_messages:
        print(f"FAILED: Expected at least {min_expected_messages} messages, got {message_count}")
        exit(1)

    # Verify messages contain expected data
    print("Verifying message structure...")
    first_message = list_sink[0]

    if b"Timestamp" not in first_message:
        print(f"FAILED: Message should contain 'Timestamp' field")
        print(f"First message content: {first_message}")
        exit(1)

    print(f"Success: Verified {message_count} messages with correct structure")
    print(f"First message sample: {first_message[:200]}...")
    exit(0)


if __name__ == "__main__":
    main()
