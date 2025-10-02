#!/usr/bin/env python3
"""
Verify SQL CDC output from Kafka.

This script validates that SQL CDC events are properly captured and published to Kafka.
"""
import os
import time
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    test_topic = os.getenv("TEST_OUTPUT_TOPIC", "test-sql-cdc-output")
    timeout = int(os.getenv("TEST_TIMEOUT", "60"))
    expected_count = int(os.getenv("TEST_MESSAGE_COUNT", "1"))

    print(f"Consuming CDC events from topic: {test_topic}")
    print(f"Expected at least {expected_count} events")

    app = Application(
        broker_address=broker_address,
        consumer_group=f"test-consumer-sql-cdc-{int(time.time())}",
        auto_offset_reset="earliest"
    )

    topic = app.topic(test_topic)
    list_sink = ListSink()

    sdf = app.dataframe(topic)
    sdf.sink(list_sink)

    # Run with timeout to collect messages
    app.run(timeout=timeout)

    message_count = len(list_sink)
    print(f"Received {message_count} CDC events from Kafka")

    if message_count < expected_count:
        print(f"FAILED: Expected >= {expected_count} CDC events, got {message_count}")
        exit(1)

    # Verify CDC event structure
    first_event = list_sink[0]
    expected_fields = {"operation", "lsn", "data"}
    actual_fields = set(first_event.keys())

    if not expected_fields.issubset(actual_fields):
        print(f"FAILED: Missing CDC fields. Expected: {expected_fields}, Got: {actual_fields}")
        exit(1)

    # Verify operation types
    operations = [event['operation'] for event in list_sink]
    print(f"CDC operations captured: {operations}")

    # Should have inserts
    if 'insert' not in operations:
        print("FAILED: No INSERT operations captured")
        exit(1)

    # Verify data structure in events
    for i, event in enumerate(list_sink):
        if 'operation' not in event:
            print(f"FAILED: Event {i} missing 'operation' field")
            exit(1)
        if 'lsn' not in event:
            print(f"FAILED: Event {i} missing 'lsn' field")
            exit(1)
        if 'data' not in event:
            print(f"FAILED: Event {i} missing 'data' field")
            exit(1)

        operation = event['operation']
        if operation not in ['insert', 'update_before', 'update_after', 'delete']:
            print(f"FAILED: Unknown operation type: {operation}")
            exit(1)

        # Verify data contains expected fields
        data = event['data']
        if 'id' not in data:
            print(f"FAILED: Event {i} data missing 'id' field")
            exit(1)
        if 'name' not in data:
            print(f"FAILED: Event {i} data missing 'name' field")
            exit(1)
        if 'value' not in data:
            print(f"FAILED: Event {i} data missing 'value' field")
            exit(1)

    # Count operation types
    insert_count = operations.count('insert')
    update_before_count = operations.count('update_before')
    update_after_count = operations.count('update_after')
    delete_count = operations.count('delete')

    print(f"CDC event breakdown:")
    print(f"  - INSERT: {insert_count}")
    print(f"  - UPDATE (before): {update_before_count}")
    print(f"  - UPDATE (after): {update_after_count}")
    print(f"  - DELETE: {delete_count}")

    if insert_count < 1:
        print(f"FAILED: Expected at least 1 INSERT, got {insert_count}")
        exit(1)

    print(f"SUCCESS: SQL CDC test passed - captured {message_count} CDC events from SQL Server")
    exit(0)


if __name__ == "__main__":
    main()
