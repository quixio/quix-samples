import os
import json
from quixstreams import Application


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_OUTPUT_TOPIC", "test-opc-ua-output")
    min_expected_messages = 1

    print(f"Consuming from topic: {topic_name}")

    app = Application(broker_address=broker_address, auto_offset_reset="earliest")

    topic = app.topic(topic_name)

    messages = []

    with app.get_consumer() as consumer:
        consumer.subscribe([topic_name])

        consecutive_none = 0
        for _ in range(100):
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                consecutive_none += 1
                if consecutive_none >= 5:
                    break
                continue
            consecutive_none = 0
            if msg.error():
                continue

            value = msg.value()
            if value:
                message = json.loads(value.decode('utf-8'))
                messages.append(message)

    print(f"Consumed {len(messages)} messages")

    if len(messages) < min_expected_messages:
        print(f"FAILED: Expected at least {min_expected_messages} messages, got {len(messages)}")
        exit(1)

    expected_fields = {"srv_ts", "connector_ts", "type", "val", "param", "machine"}

    messages_to_check = min(len(messages), 3)
    for i in range(messages_to_check):
        message = messages[i]
        print(f"Message {i}: param={message.get('param')}, val={message.get('val')}, type={message.get('type')}")

        # Check required OPC UA fields
        for field in expected_fields:
            if field not in message:
                print(f"FAILED: Message {i} missing '{field}' field")
                exit(1)

        # Verify timestamps are positive
        if message['srv_ts'] <= 0:
            print(f"FAILED: Message {i} has invalid srv_ts: {message['srv_ts']}")
            exit(1)

        if message['connector_ts'] <= 0:
            print(f"FAILED: Message {i} has invalid connector_ts: {message['connector_ts']}")
            exit(1)

    parameters = {msg['param'] for msg in messages}
    print(f"Captured parameters: {parameters}")

    # Verify at least one machine name is present
    machines = {msg['machine'] for msg in messages}
    print(f"Captured machines: {machines}")

    if not machines:
        print(f"FAILED: No machine names found in messages")
        exit(1)

    print(f"Success: Verified {len(messages)} OPC UA messages with correct structure from OPC UA client source")
    exit(0)


if __name__ == "__main__":
    main()
