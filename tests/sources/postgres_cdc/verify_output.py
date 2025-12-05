#!/usr/bin/env python3
"""
Verify that CDC messages from Postgres are published to Kafka.
Expected: INSERT, UPDATE, and DELETE operations captured.
"""
import json
import os
import sys
from quixstreams import Application

def main():
    app = Application(
        broker_address=os.environ["Quix__Broker__Address"],
        auto_offset_reset="earliest"
    )

    topic_name = os.environ["TEST_OUTPUT_TOPIC"]
    topic = app.topic(topic_name)

    consumer = app.get_consumer()
    consumer.subscribe([topic_name])

    print(f"Consuming from topic: {topic_name}")

    messages = []
    max_wait = 20
    start_time = __import__('time').time()

    expected_count = int(os.environ.get("TEST_MESSAGE_COUNT", 3))

    try:
        consecutive_none = 0
        while len(messages) < expected_count:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                consecutive_none += 1
                if consecutive_none >= 5 and len(messages) >= 3:
                    break
                if __import__('time').time() - start_time > max_wait:
                    print(f"Timeout: Only received {len(messages)} messages after {max_wait}s")
                    sys.exit(1)
                continue

            consecutive_none = 0
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            value = json.loads(msg.value().decode('utf-8'))
            messages.append(value)

    finally:
        consumer.close()

    print(f"Consumed {len(messages)} messages")

    # Verify we got the expected CDC operations
    operations = [msg.get('kind') for msg in messages]

    # Display all messages
    for i, msg in enumerate(messages):
        operation = msg.get('kind', 'unknown')
        print(f"Message {i}: Operation={operation}")
        if 'columnvalues' in msg:
            print(f"  Data: {msg['columnvalues']}")

    # Verify we have INSERT, UPDATE, and DELETE
    if 'insert' not in operations:
        print("ERROR: Missing INSERT operation")
        sys.exit(1)

    if 'update' not in operations:
        print("ERROR: Missing UPDATE operation")
        sys.exit(1)

    if 'delete' not in operations:
        print("ERROR: Missing DELETE operation")
        sys.exit(1)

    print(f"Success: Verified {len(messages)} CDC messages (INSERT, UPDATE, DELETE)")

if __name__ == "__main__":
    main()
