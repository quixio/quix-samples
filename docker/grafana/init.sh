#!/bin/sh
set -e

STATE_DIR=/app/state/grafana
RUN_USER=grafana
. /state.sh

state_exec /run.sh grafana-server --homepath=/usr/share/grafana
