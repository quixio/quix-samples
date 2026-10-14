#!/bin/sh
# Initialize MQTT broker with authentication

MQTT_USERNAME="${MQTT_USERNAME:-testuser}"
MQTT_PASSWORD="${MQTT_PASSWORD:-testpass}"
CONFIG_DIR="/app/state/mosquitto/config"
LOG_DIR="/app/state/mosquitto/log"
DATA_DIR="/app/state/mosquitto/data"

echo "Setting up MQTT broker directories..."
mkdir -p "$CONFIG_DIR" "$LOG_DIR" "$DATA_DIR"

echo "Creating password file for user: $MQTT_USERNAME"
mosquitto_passwd -b -c "$CONFIG_DIR/passwd" "$MQTT_USERNAME" "$MQTT_PASSWORD"

echo "Setting permissions for mosquitto user..."
chown -R mosquitto:mosquitto /app/state/mosquitto
chmod -R 755 /app/state/mosquitto

echo "Starting Mosquitto MQTT broker..."
exec mosquitto -c /mosquitto/config/mosquitto.conf
