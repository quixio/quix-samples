#!/bin/sh
set -e

TARGET_DIR="/app/state/mosquitto"
TARGET_USER="mosquitto"
TARGET_GROUP="mosquitto"

# Check if directory already exists
if [ ! -d "$TARGET_DIR" ]; then
  su -s /bin/sh -c "mkdir -p '$TARGET_DIR'" "$TARGET_USER" 2>/dev/null || {
    mkdir -p "$TARGET_DIR" || {
      echo "❌ Failed to create directory as root"
      exit 1
    }

    chown "$TARGET_USER:$TARGET_GROUP" "$TARGET_DIR" 2>/dev/null || {
      echo "❌ Failed to chown directory to $TARGET_USER"
      exit 1
    }
  }
fi

# Get actual uid and gid assigned
ACTUAL_DIR_UID=$(stat -c '%u' "$TARGET_DIR")
ACTUAL_DIR_GID=$(stat -c '%g' "$TARGET_DIR")

# Update user/group if needed
TARGET_USER_UID=$(id -u "$TARGET_USER")
TARGET_USER_GID=$(id -g "$TARGET_USER")

if [ "$ACTUAL_DIR_UID" -ne "$TARGET_USER_UID" ] && [ "$ACTUAL_DIR_UID" -ne 0 ]; then
  usermod -u "$ACTUAL_DIR_UID" "$TARGET_USER" || {
    echo "❌ Failed to update $TARGET_USER UID"
    exit 1
  }
fi

if [ "$ACTUAL_DIR_GID" -ne "$TARGET_USER_GID" ] && [ "$ACTUAL_DIR_GID" -ne 0 ]; then
  groupmod -g "$ACTUAL_DIR_GID" "$TARGET_GROUP" || {
    echo "❌ Failed to update $TARGET_GROUP GID"
    exit 1
  }
fi

su -s /bin/sh $TARGET_USER -c "mkdir -p $TARGET_DIR/config/ $TARGET_DIR/log/ $TARGET_DIR/data/"
su -s /bin/sh $TARGET_USER -c "mosquitto_passwd -b -c $TARGET_DIR/config/passwd $MQTT_USERNAME $MQTT_PASSWORD"
exec su -s /bin/sh $TARGET_USER -c "mosquitto -c /mosquitto/config/mosquitto.conf"
