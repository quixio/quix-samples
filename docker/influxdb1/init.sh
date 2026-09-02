#!/bin/sh
set -e

TARGET_DIR="/app/state/influxdb"

# Check if directory already exists
if [ ! -d "$TARGET_DIR" ]; then
  su -s /bin/sh -c "mkdir -p '$TARGET_DIR'" 2>/dev/null || {
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

# Set the data directory to our custom path
export INFLUXDB_DATA_DIR="$TARGET_DIR/data"
export INFLUXDB_META_DIR="$TARGET_DIR/meta"
export INFLUXDB_DATA_WAL_DIR="$TARGET_DIR/wal"

# The v1 image initialises itself from INFLUXDB_ADMIN_USER / INFLUXDB_ADMIN_PASSWORD /
# INFLUXDB_DB, but the connection is defined once in the shared influxdb1-config Variable
# Group as INFLUXDB1_*, so that clients read the same values. Map one onto the other.
export INFLUXDB_ADMIN_USER="$INFLUXDB1_USERNAME"
export INFLUXDB_ADMIN_PASSWORD="$INFLUXDB1_PASSWORD"
export INFLUXDB_DB="$INFLUXDB1_DATABASE"

# Fail if admin user or password is not set or empty
if [ -z "$INFLUXDB_ADMIN_USER" ]; then
  echo "❌ ERROR: INFLUXDB1_USERNAME is required but not set or empty"
  exit 1
fi
if [ -z "$INFLUXDB_ADMIN_PASSWORD" ]; then
  echo "❌ ERROR: INFLUXDB1_PASSWORD is required but not set or empty"
  exit 1
fi

export INFLUXDB_HTTP_AUTH_ENABLED=true

# Call the original InfluxDB entrypoint with our config
exec /entrypoint.sh influxd -config "${INFLUXD_CONFIG_PATH}"