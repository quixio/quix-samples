import asyncio
import os
import json
import base64
import websockets


async def websocket_client(received_messages, ws_host, ws_port, ws_username, ws_password, path="channel1"):
    """Connect to WebSocket server and collect received messages"""
    url = f"ws://{ws_host}:{ws_port}/{path}"

    # Create Basic Auth header
    credentials = f"{ws_username}:{ws_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {encoded_credentials}"}

    print(f"Connecting to WebSocket at {url}")

    try:
        async with websockets.connect(url, additional_headers=headers) as websocket:
            print("WebSocket connected successfully")

            try:
                async with asyncio.timeout(25):
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


async def main():
    ws_host = os.getenv("WS_HOST", "websocket-destination")
    ws_port = int(os.getenv("WS_PORT", "80"))
    ws_username = os.getenv("WS_USERNAME", "testuser")
    ws_password = os.getenv("WS_PASSWORD", "testpass")
    expected_count = int(os.getenv("TEST_MESSAGE_COUNT", "1"))

    print("Starting WebSocket client to receive messages")

    received_messages = []

    # Connect to WebSocket and receive messages
    await websocket_client(received_messages, ws_host, ws_port, ws_username, ws_password)

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

    print(f"Success: Verified {actual_count} messages received via WebSocket")
    exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
