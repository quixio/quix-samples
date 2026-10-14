#!/bin/sh
set -e

TARGET_DIR="/app/state/minio"
TARGET_USER="root"
TARGET_GROUP="root"

# Check if directory already exists
if [ ! -d "$TARGET_DIR" ]; then
  su -s /bin/sh -c "mkdir -p '$TARGET_DIR'" "$TARGET_USER" 2>/dev/null || {
    mkdir -p "$TARGET_DIR" || {
      echo "❌ Failed to create directory as root"
      exit 1
    }

    chown "$TARGET_USER:$TARGET_GROUP" "$TARGET_DIR" 2>/dev/null || {
      echo "❌ Failed to chown directory to $TARGET_USER"
      exit 1
    }
  }
fi

# MinIO's root user is also the S3 access key that clients authenticate with, so it comes
# from the shared aws-connection Variable Group (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY)
# and the S3 connectors read the same values. Map them onto the names minio expects.
export MINIO_ROOT_USER="$AWS_ACCESS_KEY_ID"
export MINIO_ROOT_PASSWORD="$AWS_SECRET_ACCESS_KEY"

if [ -z "$MINIO_ROOT_USER" ] || [ -z "$MINIO_ROOT_PASSWORD" ]; then
  echo "❌ ERROR: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required to initialise MinIO"
  exit 1
fi

exec /bin/sh -c "minio server $TARGET_DIR --console-address ':9001'"