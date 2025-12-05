import os
import time
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    output_topic = os.getenv("TEST_OUTPUT_TOPIC", "test-output")
    timeout = int(os.getenv("TEST_TIMEOUT", "30"))
    min_expected_count = int(os.getenv("TEST_MIN_EXPECTED_COUNT", "1"))

    print(f"Consuming from output topic: {output_topic}")

    app = Application(
        broker_address=broker_address,
        consumer_group=f"test-consumer-{int(time.time())}",
        auto_offset_reset="earliest"
    )

    topic = app.topic(output_topic)
    list_sink = ListSink()

    sdf = app.dataframe(topic)
    sdf.sink(list_sink)

    app.run(timeout=timeout)

    message_count = len(list_sink)
    print(f"Received {message_count} alert messages from output topic")

    if message_count < min_expected_count:
        print(f"FAILED: Expected at least {min_expected_count} alert messages, got {message_count}")
        exit(1)

    # Verify messages contain expected alert structure
    for i, message in enumerate(list_sink):
        print(f"Alert message {i}: {message}")

        if 'Timestamp' not in message:
            print(f"FAILED: Message {i} missing 'Timestamp' field")
            exit(1)
        if 'Alert' not in message:
            print(f"FAILED: Message {i} missing 'Alert' field")
            exit(1)
        if 'Title' not in message['Alert']:
            print(f"FAILED: Message {i} Alert missing 'Title' field")
            exit(1)
        if 'Message' not in message['Alert']:
            print(f"FAILED: Message {i} Alert missing 'Message' field")
            exit(1)
        if 'Hard braking detected' not in message['Alert']['Title']:
            print(f"FAILED: Message {i} has unexpected alert title")
            exit(1)

    print(f"Success: Verified {message_count} alert messages with correct structure")
    exit(0)


if __name__ == "__main__":
    main()
