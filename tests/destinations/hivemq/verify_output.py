import paho.mqtt.client as mqtt
import os
import time
import sys

messages_received = []
expected_count = 1
mqtt_broker = os.getenv("MQTT_BROKER", "mqtt-broker")
mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
mqtt_topic = os.getenv("MQTT_TOPIC", "test/output/#")

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT broker with result code {reason_code}")
    client.subscribe(mqtt_topic)
    print(f"Subscribed to topic: {mqtt_topic}")

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    messages_received.append(msg.payload)

    if len(messages_received) >= expected_count:
        print(f"Received all {expected_count} expected messages")
        client.disconnect()

def main():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Connecting to MQTT broker at {mqtt_broker}:{mqtt_port}...")
    client.connect(mqtt_broker, mqtt_port, 60)

    # Wait for messages (timeout after 45 seconds)
    start_time = time.time()
    client.loop_start()

    while len(messages_received) < expected_count:
        if time.time() - start_time > 45:
            print(f"Timeout: Only received {len(messages_received)} messages, expected at least {expected_count}")
            sys.exit(1)
        time.sleep(0.1)

    client.loop_stop()

    # Verify messages contain expected data
    for msg in messages_received:
        msg_str = msg.decode()
        if "id" not in msg_str:
            print(f"Message missing 'id' field: {msg_str}")
            sys.exit(1)

    print(f"Success: Verified {len(messages_received)} messages from MQTT")
    sys.exit(0)

if __name__ == "__main__":
    main()
