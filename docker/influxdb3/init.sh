#!/bin/sh
set -e

TARGET_DIR="/app/state/influxdb3"
TARGET_USER="influxdb3"
TARGET_GROUP="influxdb3"

# Check if directory already exists
if [ ! -d "$TARGET_DIR" ]; then
  su -s /bin/sh -c "mkdir -p '$TARGET_DIR'" "$TARGET_USER" 2>/dev/null || {
    mkdir -p "$TARGET_DIR" || {
      echo "❌ Failed to create directory as root"
      exit 1
    }

    chown "$TARGET_USER" "$TARGET_DIR" 2>/dev/null || {
      echo "❌ Failed to chown directory to $TARGET_USER"
      exit 1
    }
  }
fi

exec su -s /bin/sh $TARGET_USER -c "influxdb3 serve --without-auth --node-id node0 --object-store file --data-dir $TARGET_DIR"
