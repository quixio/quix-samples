#!/bin/sh
set -e

GEN_ARGS="
  --format=jsonlines
  --use-case=${TSBS_USE_CASE:-cpu-only}
  --seed=${TSBS_SEED:-123}
  --scale=${TSBS_SCALE:-5}
  --timestamp-start=${TSBS_TIMESTAMP_START:-2025-01-01T00:00:00Z}
  --timestamp-end=${TSBS_TIMESTAMP_END:-2025-01-01T00:10:00Z}
  --log-interval=${TSBS_LOG_INTERVAL:-10s}
"

LOAD_ARGS="
  --api-url=${Quix__Portal__Api:-https://portal-api.platform.quix.io/}
  --workspace=${Quix__Workspace__Id:?Must set Quix__Workspace__Id}
  --token=${Quix__Sdk__Token:?Must set Quix__Sdk__Token}
  --topic=${output:-tsbs_data}
"

# Execute the pipeline
exec ./bin/tsbs_generate_data $GEN_ARGS | ./bin/tsbs_load_kafka_quix $LOAD_ARGS