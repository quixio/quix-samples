#!/bin/sh
set -e

STATE_DIR=/app/state/redis
RUN_USER=redis
. /state.sh

state_exec redis-server /usr/local/etc/redis/redis.conf
