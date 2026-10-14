#!/bin/sh
set -e

TARGET_DIR="/app/state/influxdb3"
TARGET_USER="influxdb3"
TARGET_GROUP="influxdb3"
TOKEN_FILE="/app/state/influxdb3-admin-token.json"

# ---------------------------------------------------------------------------
# Configuration (injected by the "influxdb3-config" Quix global variable group)
#
#   INFLUXDB3_USE_TOKEN  'true' enables authentication; anything else runs the
#                        server WITHOUT auth (default: false).
#   INFLUXDB3_TOKEN      admin token, secret. Only used when USE_TOKEN is true,
#                        in which case it must start with 'apiv3_'.
#   INFLUXDB3_NODE_ID    optional - server node id       (default: node0)
#   INFLUXDB3_OBJECT_STORE optional - object store backend (default: file)
#
# INFLUXDB3_HOST / INFLUXDB3_DATABASE / INFLUXDB3_ORG are also injected by the
# same group but are only consumed by clients, so they are ignored here.
# ---------------------------------------------------------------------------
NODE_ID="${INFLUXDB3_NODE_ID:-node0}"
OBJECT_STORE="${INFLUXDB3_OBJECT_STORE:-file}"

# Normalise the boolean flag to 1 (on) / 0 (off).
case "${INFLUXDB3_USE_TOKEN:-false}" in
  true|True|TRUE|1|yes|Yes|YES) USE_TOKEN=1 ;;
  *) USE_TOKEN=0 ;;
esac

# When auth is requested the token must be a valid InfluxDB v3 token.
if [ "$USE_TOKEN" -eq 1 ]; then
  case "$INFLUXDB3_TOKEN" in
    apiv3_*) ;;
    *) echo "❌ INFLUXDB3_USE_TOKEN is true but INFLUXDB3_TOKEN is not a valid token (must start with 'apiv3_')."; exit 1 ;;
  esac
fi

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

SERVE="influxdb3 serve --node-id '$NODE_ID' --object-store '$OBJECT_STORE' --data-dir '$TARGET_DIR'"

if [ "$USE_TOKEN" -eq 1 ]; then
  # Write an "offline" admin-token file so the first startup bootstraps auth
  # non-interactively with our predetermined token. The same token value is
  # shared with clients via the global variable group, so they can authenticate.
  # On a persisted volume the token already exists after the first boot and this
  # file is simply ignored (the server only seeds when no admin token exists).
  EXPIRY_MILLIS=$(( ($(date +%s) + 3153600000) * 1000 ))   # ~100 years out
  cat > "$TOKEN_FILE" <<EOF
{
  "token": "$INFLUXDB3_TOKEN",
  "name": "_admin",
  "description": "Admin token for InfluxDB 3 (managed by the influxdb3-config Quix global variable group)",
  "expiry_millis": $EXPIRY_MILLIS
}
EOF
  chown "$TARGET_USER" "$TOKEN_FILE" 2>/dev/null || true
  chmod 600 "$TOKEN_FILE"
  SERVE="$SERVE --admin-token-file '$TOKEN_FILE'"
else
  echo "⚠️  INFLUXDB3_USE_TOKEN is not 'true' — starting InfluxDB v3 WITHOUT authentication."
  SERVE="$SERVE --without-auth"
fi

exec su -s /bin/sh "$TARGET_USER" -c "$SERVE"
