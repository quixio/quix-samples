#!/bin/sh
set -e

#echo "Running as: $(whoami)"
su -c "mkdir -p /app/state/influxdb2" - influxdb

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