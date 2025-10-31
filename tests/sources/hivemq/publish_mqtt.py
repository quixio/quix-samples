import os
import time
import json
import paho.mqtt.client as mqtt
import ssl

def main():
    mqtt_host = os.getenv("MQTT_HOST", "mosquitto")
    mqtt_port = int(os.getenv("MQTT_PORT", "8883"))
    message_count = int(os.getenv("TEST_MESSAGE_COUNT", "3"))

    topic = "test/topic"

    print(f"Publishing {message_count} messages to MQTT broker at {mqtt_host}:{mqtt_port}")

    # Create MQTT client
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)

    # Set username and password
    client.username_pw_set("testuser", "testpass")

    # Set TLS
    client.tls_set(ca_certs="/tests/ca.crt", tls_version=ssl.PROTOCOL_TLS)

    # Connect to broker
    print(f"Connecting to {mqtt_host}:{mqtt_port}...")
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_start()

    time.sleep(2)  # Wait for connection

    # Publish messages
    for i in range(message_count):
        payload = {
            "id": i,
            "message": f"test_message_{i}",
            "timestamp": int(time.time() * 1000)
        }

        payload_json = json.dumps(payload)

        print(f"Publishing to {topic}: {payload}")
        result = client.publish(topic, payload_json, qos=1)
        result.wait_for_publish()

        time.sleep(0.5)

    client.loop_stop()
    client.disconnect()

    print(f"Successfully published {message_count} messages")
    exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
