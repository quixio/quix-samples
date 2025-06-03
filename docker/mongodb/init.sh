#!/bin/sh
set -e

TARGET_DIR="/app/state/mongodb"
TARGET_USER="mongodb"
TARGET_GROUP="mongodb"

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
ACTUAL_UID=$(stat -c '%u' "$TARGET_DIR")
ACTUAL_GID=$(stat -c '%g' "$TARGET_DIR")

# Update user/group if needed
CURRENT_UID=$(id -u "$TARGET_USER")
CURRENT_GID=$(id -g "$TARGET_USER")

if [ "$ACTUAL_UID" -ne "$CURRENT_UID" ] && [ "$ACTUAL_UID" -ne 0 ]; then
  usermod -u "$ACTUAL_UID" "$TARGET_USER" || {
    echo "❌ Failed to update $TARGET_USER UID"
    exit 1
  }
fi

if [ "$ACTUAL_GID" -ne "$CURRENT_GID" ] && [ "$ACTUAL_GID" -ne 0 ]; then
  groupmod -g "$ACTUAL_GID" "$TARGET_GROUP" || {
    echo "❌ Failed to update $TARGET_GROUP GID"
    exit 1
  }
fi

exec su -s /bin/sh $TARGET_USER -c "docker-entrypoint.sh mongod --bind_ip_all --dbpath $TARGET_DIR"