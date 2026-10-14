import os
import time
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    broker_address = os.getenv("Quix__Broker__Address", "quix-kafka:9092")
    output_topic = os.getenv("TEST_OUTPUT_TOPIC", "replicated-topic")
    timeout = int(os.getenv("TEST_TIMEOUT", "40"))
    expected_count = 3

    print(f"Consuming from output topic: {output_topic}")
    print(f"Expected {expected_count} messages")

    app = Application(
        broker_address=broker_address,
        consumer_group=f"test-consumer-{int(time.time())}",
        auto_offset_reset="earliest"
    )

    topic = app.topic(output_topic)
    list_sink = ListSink(metadata=True)

    sdf = app.dataframe(topic)
    sdf.sink(list_sink)

    app.run(count=expected_count, timeout=timeout)

    message_count = len(list_sink)
    print(f"Received {message_count} messages from output topic")

    if message_count < expected_count:
        print(f"FAILED: Expected {expected_count} messages, got {message_count}")
        exit(1)

    print("Verifying message structure...")

    # Expected data from data.jsonlines
    expected_keys = ["test0", "test1", "test2"]
    received_keys = []

    for i, message in enumerate(list_sink):
        print(f"Message {i}: {message}")

        # Verify the message has the expected structure
        if "_key" not in message:
            print(f"FAILED: Message {i} missing '_key' field")
            exit(1)

        received_keys.append(message["_key"].decode())

        # Verify _value structure
        value = message
        if not isinstance(value, dict):
            print(f"FAILED: Message {i} _value should be a dict, got {type(value)}")
            exit(1)

        if "k0" not in value or "k1" not in value:
            print(f"FAILED: Message {i} _value missing expected fields (k0, k1)")
            exit(1)

        if value["k0"] != "v0" or value["k1"] != "v1":
            print(f"FAILED: Message {i} _value has unexpected values")
            exit(1)

    # Verify all expected keys were received
    print(f"Received keys: {received_keys}")
    print(f"Expected keys: {expected_keys}")

    for expected_key in expected_keys:
        if expected_key not in received_keys:
            print(f"FAILED: Expected key '{expected_key}' not found in messages")
            exit(1)

    print(f"Success: Verified {message_count} messages with correct structure")
    print(f"- All messages have required fields: _key, _value")
    print(f"- All expected keys present: {expected_keys}")
    print(f"- All values have correct structure and content")
    exit(0)


if __name__ == "__main__":
    main()