import asyncio
import os
import json
import base64
import time
import websockets
from quixstreams import Application


async def websocket_receiver(received_messages, ws_host, ws_port, ws_username, ws_password, path="channel1"):
    """Connect to WebSocket server and collect received messages"""
    url = f"ws://{ws_host}:{ws_port}/{path}"

    # Create Basic Auth header
    credentials = f"{ws_username}:{ws_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {encoded_credentials}"}

    print(f"WebSocket client connecting to {url}")

    try:
        async with websockets.connect(url, additional_headers=headers) as websocket:
            print("WebSocket client connected successfully")

            try:
                # Wait for messages with a timeout
                async with asyncio.timeout(20):
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        received_messages.append(data)
                        print(f"Received message: {data}")
            except asyncio.TimeoutError:
                print("WebSocket client timeout - finished receiving")
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed by server")

    except Exception as e:
        print(f"WebSocket client error: {e}")
        import traceback
        traceback.print_exc()


async def produce_messages():
    """Produce test messages to Kafka"""
    # Wait a bit for WebSocket client to be fully connected
    await asyncio.sleep(2)

    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_INPUT_TOPIC", "test-websocket-input")
    message_count = int(os.getenv("TEST_MESSAGE_COUNT", "5"))

    print(f"Producer: Producing {message_count} test messages to topic: {topic_name}")

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
            print(f"Producer: Producing message {i} with key 'channel1': {message}")

            serialized = json.dumps(message).encode('utf-8')

            producer.produce(
                topic=topic.name,
                key="channel1",  # Match the WebSocket path
                value=serialized
            )

            await asyncio.sleep(0.2)

        producer.flush()

    print(f"Producer: Successfully produced {message_count} messages")


async def main():
    ws_host = os.getenv("WS_HOST", "websocket-destination")
    ws_port = int(os.getenv("WS_PORT", "80"))
    ws_username = os.getenv("WS_USERNAME", "testuser")
    ws_password = os.getenv("WS_PASSWORD", "testpass")
    expected_count = int(os.getenv("TEST_MESSAGE_COUNT", "5"))

    received_messages = []

    # Start WebSocket receiver and producer concurrently
    # Receiver task will keep connection open and collect messages
    # Producer task will send messages after a short delay
    receiver_task = asyncio.create_task(
        websocket_receiver(received_messages, ws_host, ws_port, ws_username, ws_password)
    )
    producer_task = asyncio.create_task(produce_messages())

    # Wait for both tasks to complete
    await asyncio.gather(receiver_task, producer_task)

    # Verify results
    actual_count = len(received_messages)
    print(f"\nReceived {actual_count} messages via WebSocket")

    if actual_count < expected_count:
        print(f"FAILED: Expected at least {expected_count} messages, got {actual_count}")
        exit(1)

    messages_to_check = min(len(received_messages), 3)
    for i in range(messages_to_check):
        message = received_messages[i]
        print(f"Message {i}: {message}")

        if 'id' not in message:
            print(f"FAILED: Message {i} missing 'id' field")
            exit(1)
        if 'value' not in message:
            print(f"FAILED: Message {i} missing 'value' field")
            exit(1)

    print(f"SUCCESS: Verified {actual_count} messages received via WebSocket")
    exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
