import os
import time
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    output_topic = os.getenv("TEST_OUTPUT_TOPIC", "test-output")
    timeout = int(os.getenv("TEST_TIMEOUT", "30"))
    expected_count = int(os.getenv("TEST_EXPECTED_COUNT", "1"))

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
    print(f"Received {message_count} messages from output topic")

    if message_count < expected_count:
        print(f"FAILED: Expected at least {expected_count} messages, got {message_count}")
        exit(1)

    # Verify message structure
    for i, message in enumerate(list_sink):
        print(f"Message {i}: {message}")

        # Check required fields from MemoryUsageGenerator
        if 'm' not in message:
            print(f"FAILED: Message {i} missing 'm' field")
            exit(1)
        if 'host' not in message:
            print(f"FAILED: Message {i} missing 'host' field")
            exit(1)
        if 'used_percent' not in message:
            print(f"FAILED: Message {i} missing 'used_percent' field")
            exit(1)
        if 'time' not in message:
            print(f"FAILED: Message {i} missing 'time' field")
            exit(1)

        # Verify field values
        if message['m'] != 'mem':
            print(f"FAILED: Message {i} has incorrect 'm' value: {message['m']}")
            exit(1)
        if message['host'] not in ['host1', 'host2']:
            print(f"FAILED: Message {i} has invalid host: {message['host']}")
            exit(1)

    print(f"Success: Verified {message_count} messages with correct structure")
    exit(0)


if __name__ == "__main__":
    main()
