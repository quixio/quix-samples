import os
import json
import time
from quixstreams import Application

def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_INPUT_TOPIC", "test-tdengine-input")
    message_count = int(os.getenv("TEST_MESSAGE_COUNT", "5"))

    print(f"Producing to topic: {topic_name}")

    app = Application(broker_address=broker_address, auto_offset_reset="earliest")

    topic = app.topic(topic_name)

    messages = []
    current_time = int(time.time() * 1000)

    # Create messages with two different sensor IDs
    for i in range(message_count):
        sensor_id = f"sensor_{i % 2}"
        message = {
            "sensor_id": sensor_id,
            "temperature": 20.5 + i * 0.5,  # Non-whole numbers to ensure float format
            "humidity": 50.3 + i * 2.2,     # Non-whole numbers to ensure float format
            "timestamp": current_time + i * 100  # Increment by 100ms for each message
        }
        messages.append(message)

    with app.get_producer() as producer:
        for i, message in enumerate(messages):
            print(f"Producing message {i}: {message}")
            serialized = json.dumps(message).encode('utf-8')
            producer.produce(
                topic=topic.name,
                key=message["sensor_id"].encode('utf-8'),
                value=serialized,
            )
            time.sleep(0.1)

    print(f"Successfully produced {len(messages)} messages")
    exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
