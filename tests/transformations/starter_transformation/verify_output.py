import os
import time
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    output_topic = os.getenv("TEST_OUTPUT_TOPIC", "test-output")
    timeout = int(os.getenv("TEST_TIMEOUT", "45"))
    expected_count = int(os.getenv("TEST_EXPECTED_COUNT", "1"))

    print(f"Consuming from output topic: {output_topic}")
    print(f"Expecting at least {expected_count} message(s), timeout: {timeout}s")

    app = Application(
        broker_address=broker_address,
        consumer_group=f"test-consumer-{int(time.time())}",
        auto_offset_reset="earliest"
    )

    topic = app.topic(output_topic)
    list_sink = ListSink()

    sdf = app.dataframe(topic)
    sdf.sink(list_sink)

    app.run(timeout=timeout, count=expected_count)

    message_count = len(list_sink)
    print(f"Final count: {message_count} messages from output topic")

    if message_count < expected_count:
        print(f"FAILED: Expected at least {expected_count} message(s), got {message_count}")
        exit(1)

    # Verify messages contain expected fields
    for i, message in enumerate(list_sink):
        if 'id' not in message:
            print(f"FAILED: Message {i} missing 'id' field")
            exit(1)
        if 'value' not in message:
            print(f"FAILED: Message {i} missing 'value' field")
            exit(1)

    print(f"SUCCESS: Verified {message_count} transformed message(s) with correct fields")
    exit(0)


if __name__ == "__main__":
    main()
