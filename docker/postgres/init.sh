#!/bin/sh
set -e

STATE_DIR="$PGDATA"
RUN_USER=postgres
. /state.sh

# wal_level = logical to accept CDC
state_exec docker-entrypoint.sh postgres -c 'listen_addresses=*' -c wal_level=logical -c output_plugin_libraries=pgoutput,test_decoding,wal2json
