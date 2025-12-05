import os
import time
import json
from quixstreams import Application

def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_INPUT_TOPIC", "test-redis-input")
    message_count = int(os.getenv("TEST_MESSAGE_COUNT", "3"))

    print(f"Producing {message_count} test messages to topic: {topic_name}")

    app = Application(
        broker_address=broker_address,
        producer_extra_config={
            "allow.auto.create.topics": "true"
        }
    )

    topic = app.topic(topic_name)

    with app.get_producer() as producer:
        for i in range(message_count):
            message = {
                "key": f"msg_{i}",
                "id": i,
                "value": f"test_message_{i}",
                "timestamp": int(time.time() * 1000)
            }
            print(f"Producing message {i}: {message}")

            serialized = json.dumps(message).encode('utf-8')

            producer.produce(
                topic=topic.name,
                key=str(i),
                value=serialized
            )

        producer.flush()

    print(f"Successfully produced {message_count} messages")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
