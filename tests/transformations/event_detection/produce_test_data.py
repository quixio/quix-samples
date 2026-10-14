import os
import time
import json
from quixstreams import Application

def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_INPUT_TOPIC", "test-input")
    message_count = int(os.getenv("TEST_MESSAGE_COUNT", "10"))

    print(f"Producing {message_count} test messages to topic: {topic_name}")

    app = Application(
        broker_address=broker_address,
        producer_extra_config={
            "allow.auto.create.topics": "true"
        }
    )

    topic = app.topic(topic_name)

    with app.get_producer() as producer:
        # Produce messages with varying brake values
        # First 5 with low brake (< 0.5), next 10 with high brake (> 0.5) to trigger alerts
        last_timestamp = None
        for i in range(message_count):
            brake_value = 0.3 if i < 5 else 0.8  # Low then high
            msg_timestamp = int(time.time() * 1000)
            last_timestamp = msg_timestamp
            message = {
                "Brake": brake_value,
                "Speed": 50 + i,
                "timestamp": msg_timestamp  # QuixStreams uses lowercase 'timestamp'
            }
            print(f"Producing message {i}: Brake={brake_value}")

            serialized = json.dumps(message).encode('utf-8')

            producer.produce(
                topic=topic.name,
                key=str(i),
                value=serialized,
                timestamp=msg_timestamp  # Set Kafka message timestamp
            )

            # Small delay to ensure messages are spread over time for windowing
            time.sleep(0.05)  # Faster to create tighter windows

        # Produce one more dummy message with timestamp 2 seconds after the last message
        # This will close all open windows so they emit their final results
        # Important: Must include Brake field so it passes the filter before windowing
        dummy_timestamp = last_timestamp + 2000  # Add 2 seconds in milliseconds
        dummy_message = {
            "Brake": 0.0,  # Must have Brake field to pass filter
            "Speed": 0,
            "timestamp": dummy_timestamp
        }
        print(f"Producing dummy message with timestamp {dummy_timestamp} to close windows")
        serialized_dummy = json.dumps(dummy_message).encode('utf-8')
        producer.produce(
            topic=topic.name,
            key="dummy",
            value=serialized_dummy,
            timestamp=dummy_timestamp
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
