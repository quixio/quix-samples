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

# Unset empty auth variables
if [ -z "$INFLUXDB_ADMIN_USER" ]; then
  unset INFLUXDB_ADMIN_USER
fi
if [ -z "$INFLUXDB_ADMIN_PASSWORD" ]; then
  unset INFLUXDB_ADMIN_PASSWORD
fi

# Auto-enable HTTP auth if both user and password are set
if [ -n "$INFLUXDB_ADMIN_USER" ] && [ -n "$INFLUXDB_ADMIN_PASSWORD" ]; then
  export INFLUXDB_HTTP_AUTH_ENABLED=true
fi

# Call the original InfluxDB entrypoint with our config
exec /entrypoint.sh influxd -config "${INFLUXD_CONFIG_PATH}"