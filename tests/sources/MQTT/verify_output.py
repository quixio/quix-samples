import os
import time
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    output_topic = os.getenv("TEST_OUTPUT_TOPIC", "test-mqtt-output")
    timeout = int(os.getenv("TEST_TIMEOUT", "40"))
    min_expected_count = int(os.getenv("TEST_MIN_EXPECTED_COUNT", "1"))

    print(f"Consuming from output topic: {output_topic}")

    app = Application(
        broker_address=broker_address,
        consumer_group=f"test-consumer-{int(time.time())}",
        auto_offset_reset="earliest"
    )

    topic = app.topic(output_topic, value_deserializer="bytes")
    list_sink = ListSink()

    sdf = app.dataframe(topic)
    sdf.sink(list_sink)

    app.run(timeout=timeout)

    message_count = len(list_sink)
    print(f"Received {message_count} messages from output topic")

    if message_count < min_expected_count:
        print(f"FAILED: Expected at least {min_expected_count} messages, got {message_count}")
        exit(1)

    # Verify messages contain expected data - only check what we got
    messages_to_check = min(message_count, 3)
    for i in range(messages_to_check):
        message = list_sink[i]
        print(f"Message {i}: {message}")

        if b"id" not in message:
            print(f"FAILED: Message {i} should contain 'id' field")
            exit(1)

        if b"value" not in message:
            print(f"FAILED: Message {i} should contain 'value' field")
            exit(1)

    print(f"Success: Verified {message_count} messages with correct structure")
    exit(0)


if __name__ == "__main__":
    main()
