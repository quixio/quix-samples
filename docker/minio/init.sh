#!/bin/sh
set -e

STATE_DIR=/app/state/minio
. /state.sh

# MinIO's root user is also the S3 access key that clients authenticate with, so it comes
# from the shared aws-connection Variable Group (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY)
# and the S3 connectors read the same values. Map them onto the names minio expects.
export MINIO_ROOT_USER="$AWS_ACCESS_KEY_ID"
export MINIO_ROOT_PASSWORD="$AWS_SECRET_ACCESS_KEY"

if [ -z "$MINIO_ROOT_USER" ] || [ -z "$MINIO_ROOT_PASSWORD" ]; then
  echo "❌ ERROR: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required to initialise MinIO"
  exit 1
fi

exec minio server "$STATE_DIR" --console-address :9001
