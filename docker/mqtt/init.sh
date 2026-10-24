#!/bin/sh
set -e

STATE_DIR=/app/state/mosquitto
RUN_USER=mosquitto
. /state.sh

# Credentials come from the shared mqtt-connection Variable Group, so the broker and
# every client (source/sink) authenticate with the same user.
BROKER_USERNAME="$mqtt_username"
BROKER_PASSWORD="$mqtt_password"

if [ -z "$BROKER_USERNAME" ] || [ -z "$BROKER_PASSWORD" ]; then
  echo "❌ ERROR: mqtt_username and mqtt_password are required (mosquitto.conf sets allow_anonymous false)"
  exit 1
fi

mkdir -p "$STATE_DIR/config" "$STATE_DIR/log" "$STATE_DIR/data"
mosquitto_passwd -b -c "$STATE_DIR/config/passwd" "$BROKER_USERNAME" "$BROKER_PASSWORD"
state_exec mosquitto -c /mosquitto/config/mosquitto.conf
