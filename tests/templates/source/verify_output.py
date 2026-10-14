"""
Test verifier for [APP_NAME] source output.

This script:
1. Consumes messages from the Kafka output topic
2. Validates message count meets minimum expectations
3. Verifies message structure and field values
4. Exits with code 0 on success, 1 on failure

TODO: Replace all [PLACEHOLDERS] with your actual values
TODO: Customize field validations in the verification loop
"""
import os
import time
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    # ===== ENVIRONMENT VARIABLES =====
    # These are set in docker-compose.test.yml
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    output_topic = os.getenv("TEST_OUTPUT_TOPIC", "test-output")  # TODO: Update default if needed
    timeout = int(os.getenv("TEST_TIMEOUT", "30"))  # TODO: Adjust timeout if your source needs more time
    expected_count = int(os.getenv("TEST_EXPECTED_COUNT", "10"))  # TODO: Set expected message count

    print(f"Consuming from output topic: {output_topic}")

    # ===== KAFKA CONSUMER SETUP =====
    app = Application(
        broker_address=broker_address,
        consumer_group=f"test-consumer-{int(time.time())}",  # Unique consumer group per test run
        auto_offset_reset="earliest"  # Read from beginning of topic
    )

    topic = app.topic(output_topic)
    list_sink = ListSink()

    sdf = app.dataframe(topic)
    sdf.sink(list_sink)

    # Run consumer with timeout
    app.run(timeout=timeout)

    # ===== VALIDATE MESSAGE COUNT =====
    message_count = len(list_sink)
    print(f"Received {message_count} messages from output topic")

    if message_count < expected_count:
        print(f"FAILED: Expected at least {expected_count} messages, got {message_count}")
        exit(1)

    # ===== VALIDATE MESSAGE STRUCTURE AND CONTENT =====
    for i, message in enumerate(list_sink):
        print(f"Message {i}: {message}")

        # TODO: Add validation for each required field in your messages
        # PATTERN: Check field exists
        if '[field1_name]' not in message:  # TODO: Replace '[field1_name]' with your actual field name (e.g., 'sensor_id')
            print(f"FAILED: Message {i} missing '[field1_name]' field")
            exit(1)

        if '[field2_name]' not in message:  # TODO: Replace '[field2_name]' with your actual field name (e.g., 'temperature')
            print(f"FAILED: Message {i} missing '[field2_name]' field")
            exit(1)

        # TODO: Add more field existence checks as needed
        # COPY THE PATTERN ABOVE for each required field

        # PATTERN: Validate field values
        # EXAMPLE: Validate string field has expected value
        if message['[field1_name]'] not in ['[value1]', '[value2]']:  # TODO: Replace with your validation logic
            print(f"FAILED: Message {i} has invalid [field1_name]: {message['[field1_name]']}")
            exit(1)

        # EXAMPLE: Validate numeric field is in expected range
        if not (0 <= message['[field2_name]'] <= 100):  # TODO: Replace with your validation logic
            print(f"FAILED: Message {i} has [field2_name] out of range: {message['[field2_name]']}")
            exit(1)

        # EXAMPLE: Validate field type
        if not isinstance(message['[field3_name]'], int):  # TODO: Replace with your validation logic
            print(f"FAILED: Message {i} [field3_name] is not an integer: {type(message['[field3_name]'])}")
            exit(1)

        # TODO: Add more field value validations as needed
        # Common validation patterns:
        # - String enumeration: if value not in ['option1', 'option2']: ...
        # - Numeric range: if not (min <= value <= max): ...
        # - Type checking: if not isinstance(value, expected_type): ...
        # - Format validation: if not re.match(pattern, value): ...
        # - Relationship checks: if message['field1'] > message['field2']: ...

    print(f"Success: Verified {message_count} messages with correct structure")
    exit(0)


if __name__ == "__main__":
    main()
