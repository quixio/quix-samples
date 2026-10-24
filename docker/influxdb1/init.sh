#!/bin/sh
set -e

STATE_DIR=/app/state/influxdb
RUN_USER=influxdb
. /state.sh

# Set the data directory to our custom path
export INFLUXDB_DATA_DIR="$STATE_DIR/data"
export INFLUXDB_META_DIR="$STATE_DIR/meta"
export INFLUXDB_DATA_WAL_DIR="$STATE_DIR/wal"

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

state_exec /entrypoint.sh influxd -config "${INFLUXD_CONFIG_PATH}"
