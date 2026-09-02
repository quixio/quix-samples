#!/bin/sh
set -e

TARGET_DIR="/app/state/influxdb2"
TARGET_USER="influxdb"
TARGET_GROUP="influxdb"

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

# The v2 image is set up from DOCKER_INFLUXDB_INIT_*, but the connection is defined once
# in the shared influxdb2-config Variable Group as INFLUXDB2_*. Map one onto the other,
# keeping the legacy names as a fallback so deployments created before the rename keep
# working. Username and org also have image defaults set in the dockerfile.
export DOCKER_INFLUXDB_INIT_ADMIN_TOKEN="${INFLUXDB2_TOKEN:-$DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}"
export DOCKER_INFLUXDB_INIT_PASSWORD="${INFLUXDB2_PASSWORD:-$DOCKER_INFLUXDB_INIT_PASSWORD}"
export DOCKER_INFLUXDB_INIT_BUCKET="${INFLUXDB2_BUCKET:-$DOCKER_INFLUXDB_INIT_BUCKET}"
export DOCKER_INFLUXDB_INIT_USERNAME="${INFLUXDB2_USERNAME:-$DOCKER_INFLUXDB_INIT_USERNAME}"
export DOCKER_INFLUXDB_INIT_ORG="${INFLUXDB2_ORG:-$DOCKER_INFLUXDB_INIT_ORG}"

if [ -z "$DOCKER_INFLUXDB_INIT_ADMIN_TOKEN" ] || [ -z "$DOCKER_INFLUXDB_INIT_PASSWORD" ]; then
  echo "❌ ERROR: INFLUXDB2_TOKEN and INFLUXDB2_PASSWORD are required to set up InfluxDB v2"
  exit 1
fi

# Launch the influx setup in the background.
(
    #echo "Waiting for InfluxDB to be available at localhost:8086..."
    until curl -s localhost:8086/health | grep -q '"status":"pass"'; do
    sleep 0.5
    done

    #echo "InfluxDB is available, running setup..."
    if influx setup \
    --username "${DOCKER_INFLUXDB_INIT_USERNAME}" \
    --password "${DOCKER_INFLUXDB_INIT_PASSWORD}" \
    --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
    --org "${DOCKER_INFLUXDB_INIT_ORG}" \
    --bucket "${DOCKER_INFLUXDB_INIT_BUCKET}" \
    --force 2>/dev/null; then
    echo "Setup succeeded"
    else
    #    echo "Setup failed or already set up, continuing..."
        :
    fi
) &

# Replace the shell with influxd as the primary process.
exec influxd