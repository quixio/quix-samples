import os
import time
import json
from quixstreams import Application


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_INPUT_TOPIC", "test-websocket-input")
    message_count = int(os.getenv("TEST_MESSAGE_COUNT", "5"))

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
                "id": i,
                "value": f"test_value_{i}",
                "timestamp": int(time.time() * 1000)
            }
            print(f"Producing message {i} with key 'channel1': {message}")

            serialized = json.dumps(message).encode('utf-8')

            producer.produce(
                topic=topic.name,
                key="channel1",  # Match the WebSocket path
                value=serialized
            )

            time.sleep(0.1)

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
