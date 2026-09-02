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

# The mongo image initialises its root user from MONGO_INITDB_ROOT_USERNAME /
# MONGO_INITDB_ROOT_PASSWORD, but the connection is defined once in the shared
# mongodb-connection Variable Group as MONGO_USER / MONGO_PASSWORD. Map one onto the
# other, keeping the legacy names as a fallback so deployments created before the
# rename keep working.
export MONGO_INITDB_ROOT_USERNAME="${MONGO_USER:-$MONGO_INITDB_ROOT_USERNAME}"
export MONGO_INITDB_ROOT_PASSWORD="${MONGO_PASSWORD:-$MONGO_INITDB_ROOT_PASSWORD}"

if [ -z "$MONGO_INITDB_ROOT_USERNAME" ] || [ -z "$MONGO_INITDB_ROOT_PASSWORD" ]; then
  echo "❌ ERROR: MONGO_USER and MONGO_PASSWORD are required to initialise MongoDB"
  exit 1
fi

exec su -s /bin/sh $TARGET_USER -c "docker-entrypoint.sh mongod --bind_ip_all --dbpath $TARGET_DIR"