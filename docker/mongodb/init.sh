#!/bin/sh
set -e

STATE_DIR="${MONGO_DBPATH:-/app/state/mongodb}"
RUN_USER=mongodb
. /state.sh

# The mongo image initialises its root user from MONGO_INITDB_ROOT_USERNAME /
# MONGO_INITDB_ROOT_PASSWORD, but the connection is defined once in the shared
# mongodb-connection Variable Group as MONGO_USER / MONGO_PASSWORD, so that the sink and
# other clients read the same values. Map one onto the other.
export MONGO_INITDB_ROOT_USERNAME="$MONGO_USER"
export MONGO_INITDB_ROOT_PASSWORD="$MONGO_PASSWORD"

if [ -z "$MONGO_INITDB_ROOT_USERNAME" ] || [ -z "$MONGO_INITDB_ROOT_PASSWORD" ]; then
  echo "❌ ERROR: MONGO_USER and MONGO_PASSWORD are required - is the mongodb-connection variable group assigned?"
  exit 1
fi

state_exec docker-entrypoint.sh mongod --bind_ip_all --dbpath "$STATE_DIR"
