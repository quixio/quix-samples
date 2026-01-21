import paho.mqtt.client as paho
import os
import time
import sys

messages_received = []
expected_count = int(os.getenv("TEST_MESSAGE_COUNT", "1"))
mqtt_broker = os.getenv("MQTT_BROKER", "mqtt-broker")
mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
mqtt_topic = os.getenv("MQTT_TOPIC", "test/output/#")
mqtt_username = os.environ["MQTT_USERNAME"]
mqtt_password = os.environ["MQTT_PASSWORD"]


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT broker with result code {reason_code}")
    client.subscribe(mqtt_topic)
    print(f"Subscribed to topic: {mqtt_topic}")


def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    messages_received.append(msg.payload)


def main():
    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(mqtt_username, mqtt_password)

    print(f"Connecting to MQTT broker at {mqtt_broker}:{mqtt_port}...")
    client.connect(mqtt_broker, mqtt_port, 60)

    start_time = time.time()
    timeout = 35
    client.loop_start()

    while time.time() - start_time < timeout:
        if len(messages_received) >= expected_count:
            time.sleep(2)
            break
        time.sleep(0.5)

    client.loop_stop()

    # Verify we received at least the minimum messages
    actual_count = len(messages_received)
    if actual_count < expected_count:
        print(f"FAILED: Expected at least {expected_count} messages, got {actual_count}")
        sys.exit(1)

    messages_to_check = min(len(messages_received), 3)
    for i in range(messages_to_check):
        msg_str = messages_received[i].decode()
        print(f"Message {i}: {msg_str}")
        if "id" not in msg_str:
            print(f"FAILED: Message {i} missing 'id' field: {msg_str}")
            sys.exit(1)

    print(f"Success: Verified {actual_count} messages from MQTT")
    sys.exit(0)

if __name__ == "__main__":
    main()
