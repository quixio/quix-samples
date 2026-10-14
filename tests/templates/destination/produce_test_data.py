"""
Test data producer for [APP_NAME] destination.

This script:
1. Produces test messages to Kafka input topic
2. Messages are designed to test [APP_NAME]'s ability to [BEHAVIOR]
3. Exits with code 0 on success, 1 on failure

TODO: Replace all [PLACEHOLDERS] with your actual values
TODO: Customize message structure to match what your destination expects
"""
import os
import time
import json
from quixstreams import Application

def main():
    # ===== ENVIRONMENT VARIABLES =====
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_INPUT_TOPIC", "test-input")  # TODO: Update default if needed
    message_count = int(os.getenv("TEST_MESSAGE_COUNT", "5"))  # TODO: Set number of test messages

    print(f"Producing {message_count} test messages to topic: {topic_name}")

    # ===== KAFKA PRODUCER SETUP =====
    app = Application(
        broker_address=broker_address,
        producer_extra_config={
            "allow.auto.create.topics": "true"
        }
    )

    topic = app.topic(topic_name)

    with app.get_producer() as producer:
        # ===== PRODUCE TEST MESSAGES =====
        for i in range(message_count):
            # TODO: Customize message structure to match your destination's expectations
            message = {
                "[field1_name]": f"[value_pattern_{i}]",  # TODO: Replace with your field and value pattern
                # EXAMPLE: "sensor_id": f"sensor_{i % 2}",  # Alternates between sensor_0 and sensor_1

                "[field2_name]": 0.0 + i,  # TODO: Replace with your numeric field and pattern
                # EXAMPLE: "temperature": 20.0 + i,  # Temperature increases by 1 each message

                "[field3_name]": 0.0 + i * 2,  # TODO: Replace with another field
                # EXAMPLE: "humidity": 50.0 + i * 2,  # Humidity increases by 2 each message

                "timestamp": int(time.time() * 1000)  # DO NOT REMOVE: timestamp is often needed
            }

            # TODO: Add more fields as needed for your destination
            # Common patterns:
            # - String identifiers: f"id_{i}", f"device_{i % N}"  (cycles through N values)
            # - Incrementing numbers: start + i, start + i * step
            # - Random-ish values: (i * 7) % max_value
            # - Boolean alternating: i % 2 == 0
            # - Nested objects: {"nested": {"field": value}}
            # - Arrays: [value1, value2, value3]

            print(f"Producing message {i}: {message}")

            # Serialize message to JSON
            serialized = json.dumps(message).encode('utf-8')

            # Produce to Kafka
            producer.produce(
                topic=topic.name,
                key=str(i),
                value=serialized
            )

            # Small delay to ensure unique timestamps if needed
            time.sleep(0.01)  # TODO: Adjust or remove based on your needs

        # Ensure all messages are sent before exiting
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
