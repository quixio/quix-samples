#!/bin/sh
set -e

STATE_DIR=/app/state/influxdb2
. /state.sh

# The v2 image is set up from DOCKER_INFLUXDB_INIT_*, but the connection is defined once
# in the shared influxdb2-config Variable Group as INFLUXDB2_*, so that clients and
# Grafana read the same values. Map one onto the other. These overwrite the dockerfile's
# ENV defaults, so every one is validated below rather than silently becoming empty.
export DOCKER_INFLUXDB_INIT_ADMIN_TOKEN="$INFLUXDB2_TOKEN"
export DOCKER_INFLUXDB_INIT_PASSWORD="$INFLUXDB2_PASSWORD"
export DOCKER_INFLUXDB_INIT_BUCKET="$INFLUXDB2_BUCKET"
export DOCKER_INFLUXDB_INIT_USERNAME="$INFLUXDB2_USERNAME"
export DOCKER_INFLUXDB_INIT_ORG="$INFLUXDB2_ORG"

for required in INFLUXDB2_TOKEN INFLUXDB2_PASSWORD INFLUXDB2_BUCKET INFLUXDB2_USERNAME INFLUXDB2_ORG; do
  eval "value=\$$required"
  if [ -z "$value" ]; then
    echo "❌ ERROR: $required is required to set up InfluxDB v2 - is the influxdb2-config variable group assigned?"
    exit 1
  fi
done

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
