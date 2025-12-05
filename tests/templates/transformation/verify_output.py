"""
Test verifier for [APP_NAME] transformation output.

This script:
1. Consumes messages from the Kafka output topic
2. Validates message count meets expectations
3. Verifies transformed message structure and values
4. Exits with code 0 on success, 1 on failure

TODO: Replace all [PLACEHOLDERS] with your actual values
TODO: Customize field validations based on transformation output
"""
import os
import time
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    # ===== ENVIRONMENT VARIABLES =====
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    output_topic = os.getenv("TEST_OUTPUT_TOPIC", "test-output")  # TODO: Update default if needed
    timeout = int(os.getenv("TEST_TIMEOUT", "30"))  # TODO: Adjust timeout if transformation needs more time

    # TODO: Choose appropriate count expectation based on transformation behavior
    # Use TEST_MIN_EXPECTED_COUNT if transformation filters/aggregates (output < input)
    # Use TEST_EXPECTED_COUNT if transformation preserves all messages (output == input)
    min_expected_count = int(os.getenv("TEST_MIN_EXPECTED_COUNT", "1"))
    # OR
    # expected_count = int(os.getenv("TEST_EXPECTED_COUNT", "10"))  # For transformations that preserve all messages

    print(f"Consuming from output topic: {output_topic}")

    # ===== KAFKA CONSUMER SETUP =====
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

    # ===== VALIDATE MESSAGE COUNT =====
    message_count = len(list_sink)
    print(f"Received {message_count} transformed messages from output topic")

    # TODO: Choose appropriate count validation based on transformation behavior
    if message_count < min_expected_count:
        print(f"FAILED: Expected at least {min_expected_count} messages, got {message_count}")
        exit(1)

    # ALTERNATIVE: For transformations that preserve all messages
    # if message_count < expected_count:
    #     print(f"FAILED: Expected at least {expected_count} messages, got {message_count}")
    #     exit(1)

    # ===== VALIDATE TRANSFORMED MESSAGE STRUCTURE AND CONTENT =====
    for i, message in enumerate(list_sink):
        print(f"Transformed message {i}: {message}")

        # TODO: Validate output fields exist
        # Check fields that should be present in transformed output
        if '[output_field1]' not in message:  # TODO: Replace with actual output field
            print(f"FAILED: Message {i} missing '[output_field1]' field")
            exit(1)

        if '[output_field2]' not in message:  # TODO: Replace with actual output field
            print(f"FAILED: Message {i} missing '[output_field2]' field")
            exit(1)

        # TODO: Add more field existence checks

        # TODO: Validate transformation results
        # PATTERN for preserved fields (passed through unchanged):
        # if message['[preserved_field]'] not in ['expected_value1', 'expected_value2']:
        #     print(f"FAILED: Message {i} has invalid [preserved_field]: {message['[preserved_field]']}")
        #     exit(1)

        # PATTERN for transformed numeric fields:
        # if not (min_value <= message['[transformed_field]'] <= max_value):
        #     print(f"FAILED: Message {i} [transformed_field] out of expected range: {message['[transformed_field]']}")
        #     exit(1)

        # PATTERN for added/computed fields:
        # if '[computed_field]' not in message:
        #     print(f"FAILED: Message {i} missing computed '[computed_field]' field")
        #     exit(1)

        # PATTERN for nested objects (e.g., alerts):
        # if '[nested_object]' not in message:
        #     print(f"FAILED: Message {i} missing '[nested_object]' object")
        #     exit(1)
        # if '[nested_field]' not in message['[nested_object]']:
        #     print(f"FAILED: Message {i} [nested_object] missing '[nested_field]' field")
        #     exit(1)

        # EXAMPLE: Validate alert structure
        # if 'Alert' not in message:
        #     print(f"FAILED: Message {i} missing 'Alert' field")
        #     exit(1)
        # if 'Title' not in message['Alert']:
        #     print(f"FAILED: Message {i} Alert missing 'Title' field")
        #     exit(1)
        # if 'hard braking detected' not in message['Alert']['Title'].lower():
        #     print(f"FAILED: Message {i} has unexpected alert title")
        #     exit(1)

        # EXAMPLE: Validate windowed aggregation result
        # if 'avg_value' not in message:
        #     print(f"FAILED: Message {i} missing 'avg_value' field")
        #     exit(1)
        # if not isinstance(message['avg_value'], (int, float)):
        #     print(f"FAILED: Message {i} avg_value is not numeric: {type(message['avg_value'])}")
        #     exit(1)

        # EXAMPLE: Validate enrichment added data
        # if 'enriched_data' not in message:
        #     print(f"FAILED: Message {i} missing 'enriched_data' field")
        #     exit(1)

        # TODO: Add transformation-specific validations
        # Common patterns:
        # - Aggregation results: Check aggregated values are correct type and in expected range
        # - Filtering: Verify only expected messages made it through
        # - Enrichment: Check added fields exist and have valid data
        # - Format conversion: Validate new format/structure
        # - Windowing: Check window boundaries and results

    print(f"Success: Verified {message_count} transformed messages with correct structure")
    exit(0)


if __name__ == "__main__":
    main()
