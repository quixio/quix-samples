import os
import json
from quixstreams import Application

def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_OUTPUT_TOPIC", "test-hivemq-output")
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
            key = msg.key()
            if value:
                # The payload is forwarded as-is (bytes), so decode it
                message = json.loads(value.decode('utf-8'))
                messages.append({
                    "key": key.decode('utf-8') if key else None,
                    "value": message
                })

    print(f"Consumed {len(messages)} messages")

    if len(messages) < min_expected_messages:
        print(f"FAILED: Expected at least {min_expected_messages} messages, got {len(messages)}")
        exit(1)

    messages_to_check = min(len(messages), 3)
    for i in range(messages_to_check):
        msg = messages[i]
        message = msg["value"]
        key = msg["key"]
        print(f"Message {i} (key={key}): {message}")

        if 'id' not in message:
            print(f"FAILED: Message {i} missing 'id' field")
            exit(1)
        if 'message' not in message:
            print(f"FAILED: Message {i} missing 'message' field")
            exit(1)

        # Verify key is derived from MQTT topic
        if key != "test-topic":
            print(f"FAILED: Expected key 'test-topic' (MQTT topic with / replaced), got '{key}'")
            exit(1)

    print(f"Success: Verified {len(messages)} messages from HiveMQ MQTT source")
    exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
