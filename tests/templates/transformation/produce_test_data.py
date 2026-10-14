"""
Test data producer for [APP_NAME] transformation.

This script:
1. Produces test messages to Kafka input topic
2. Messages are designed to test [APP_NAME]'s [TRANSFORMATION_BEHAVIOR]
3. Exits with code 0 on success, 1 on failure

TODO: Replace all [PLACEHOLDERS] with your actual values
TODO: Customize message structure to match what your transformation expects as input
"""
import os
import time
import json
from quixstreams import Application

def main():
    # ===== ENVIRONMENT VARIABLES =====
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_INPUT_TOPIC", "test-input")  # TODO: Update default if needed
    message_count = int(os.getenv("TEST_MESSAGE_COUNT", "10"))  # TODO: Set number of test messages

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
        # TODO: Design test data to exercise your transformation logic
        last_timestamp = None

        for i in range(message_count):
            # TODO: Vary values to test different transformation scenarios
            msg_timestamp = int(time.time() * 1000)
            last_timestamp = msg_timestamp

            # TODO: Customize message structure for your transformation's input
            message = {
                "[input_field1]": f"[value_pattern_{i}]",  # TODO: Replace with your input field
                # EXAMPLE: "sensor_id": f"sensor_{i % 2}",  # Alternates between 2 sensors

                "[input_field2]": 0.0 + i,  # TODO: Replace with numeric field
                # EXAMPLE: "value": 0.5 + (i * 0.1),  # Gradually increasing value

                "timestamp": msg_timestamp  # Usually required for QuixStreams - lowercase 'timestamp'
            }

            # TODO: Add test data patterns based on transformation logic
            # EXAMPLE for threshold detection: Vary values above/below threshold
            # if i < 5:
            #     message["value"] = 0.3  # Below threshold
            # else:
            #     message["value"] = 0.8  # Above threshold to trigger alert

            # EXAMPLE for windowing: Add field that window aggregates
            # message["reading"] = 10 + i
            # message["Speed"] = 50 + i

            # EXAMPLE for filtering: Include mix of valid/invalid messages
            # message["status"] = "active" if i % 2 == 0 else "inactive"

            print(f"Producing message {i}: {message}")

            # Serialize message to JSON
            serialized = json.dumps(message).encode('utf-8')

            # Produce to Kafka with timestamp
            producer.produce(
                topic=topic.name,
                key=str(i),
                value=serialized,
                timestamp=msg_timestamp  # Set Kafka message timestamp for windowing
            )

            # Small delay between messages
            time.sleep(0.05)  # TODO: Adjust based on transformation needs (faster for windowing, slower for rate-limited APIs)

        # TODO: If transformation uses windowing, add dummy message to close windows
        # IMPORTANT: Dummy message must pass any filters before windowing
        # EXAMPLE:
        # if last_timestamp:
        #     dummy_timestamp = last_timestamp + 2000  # 2 seconds after last message
        #     dummy_message = {
        #         "[input_field1]": "dummy",
        #         "[input_field2]": 0.0,  # Must have required fields to pass filters
        #         "timestamp": dummy_timestamp
        #     }
        #     print(f"Producing dummy message with timestamp {dummy_timestamp} to close windows")
        #     serialized_dummy = json.dumps(dummy_message).encode('utf-8')
        #     producer.produce(
        #         topic=topic.name,
        #         key="dummy",
        #         value=serialized_dummy,
        #         timestamp=dummy_timestamp
        #     )

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
