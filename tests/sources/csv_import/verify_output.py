import os
import json
from quixstreams import Application

def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_OUTPUT_TOPIC", "test-csv-output")
    min_expected_messages = 100

    print(f"Consuming from topic: {topic_name}")
    print(f"Expected at least {min_expected_messages} messages")

    app = Application(broker_address=broker_address, auto_offset_reset="earliest")

    messages = []

    with app.get_consumer() as consumer:
        consumer.subscribe([topic_name])

        consecutive_none = 0
        for _ in range(300):
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
                message = json.loads(value.decode("utf-8"))
                messages.append(message)

    print(f"Consumed {len(messages)} messages")

    if len(messages) < min_expected_messages:
        print(f"FAILED: Expected at least {min_expected_messages} messages, got {len(messages)}")
        exit(1)

    # Verify message structure
    expected_fields = {"name", "age", "city", "score"}
    for i, message in enumerate(messages[:10]):
        actual_fields = set(message.keys())
        if not expected_fields.issubset(actual_fields):
            print(f"FAILED: Message {i} missing fields. Expected: {expected_fields}, Got: {actual_fields}")
            exit(1)

        if not isinstance(message["name"], str):
            print(f"FAILED: Message {i} 'name' should be string, got {type(message['name'])}")
            exit(1)

        if not isinstance(message["age"], (int, float)):
            print(f"FAILED: Message {i} 'age' should be numeric, got {type(message['age'])}")
            exit(1)

        if not isinstance(message["city"], str):
            print(f"FAILED: Message {i} 'city' should be string, got {type(message['city'])}")
            exit(1)

        if not isinstance(message["score"], (int, float)):
            print(f"FAILED: Message {i} 'score' should be numeric, got {type(message['score'])}")
            exit(1)

    # Verify data variety
    unique_names = set(msg["name"] for msg in messages)
    unique_cities = set(msg["city"] for msg in messages)
    print(f"Data variety: {len(unique_names)} unique names, {len(unique_cities)} unique cities")

    if len(unique_names) < 2:
        print("FAILED: Expected variety in names")
        exit(1)

    print(f"Success: Verified {len(messages)} messages with correct structure")
    exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
