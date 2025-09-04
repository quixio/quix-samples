#!/usr/bin/env bash

if [ -z "$CONNECTOR_NAME" ] || [ "$CONNECTOR_NAME" == "connector-name" ]; then
    echo "Error: CONNECTOR_NAME environment variable is required but not set."
    echo "Please specify a Confluent Hub connector name (e.g., snowflakeinc/snowflake-kafka-connector:2.1.2)"
    exit 1
fi

echo "Downloading connector: $CONNECTOR_NAME"

# Ensure plugins directory exists
mkdir -p /opt/kafka/plugins

# Determine which config file to use based on CONNECT_MODE
if [ -z "$CONNECT_MODE" ] || [ "$CONNECT_MODE" == "standalone" ]; then
    WORKER_CONFIG="/opt/kafka/config/connect-standalone.properties"
else
    WORKER_CONFIG="/opt/kafka/config/connect-distributed.properties"
fi

echo "Using worker config: $WORKER_CONFIG"
echo "Installing to: /opt/kafka/plugins"

# Install connector with required flags
/opt/confluent/bin/confluent-hub install "$CONNECTOR_NAME" \
    --no-prompt \
    --component-dir /opt/kafka/plugins \
    --worker-configs $WORKER_CONFIG

if [ $? -eq 0 ]; then
    echo "Connector $CONNECTOR_NAME installed successfully"
    ls -la /opt/kafka/plugins/
else
    echo "Error: Failed to install connector $CONNECTOR_NAME"
    echo "Debug info:"
    echo "  - Plugin directory: /opt/kafka/plugins"
    echo "  - Worker config: $WORKER_CONFIG"
    echo "  - Connector name: $CONNECTOR_NAME"
    exit 1
fi
