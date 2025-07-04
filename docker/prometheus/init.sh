#!/bin/sh
set -e

TARGET_DIR="/app/state/prom"
TARGET_USER="nobody"

# Check if directory already exists
if [ ! -d "$TARGET_DIR" ]; then
  su -s /bin/sh -c "mkdir -p '$TARGET_DIR'" "$TARGET_USER" 2>/dev/null || {
    mkdir -p "$TARGET_DIR" || {
      echo "❌ Failed to create directory as root"
      exit 1
    }

    chown "$TARGET_USER" "$TARGET_DIR" 2>/dev/null || {
      echo "❌ Failed to chown directory to $TARGET_USER"
      exit 1
    }
  }
fi

exec su -s /bin/sh $TARGET_USER -c "/bin/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/app/state/prom --storage.tsdb.retention.size=1GB"