#!/bin/sh
set -e

STATE_DIR=/app/state/prom
RUN_USER=nobody
. /state.sh

state_exec /bin/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path="$STATE_DIR" --storage.tsdb.retention.size=1GB
