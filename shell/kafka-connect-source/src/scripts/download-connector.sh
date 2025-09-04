#!/usr/bin/env bash

if [ -z "$CONNECTOR_NAME" ] || [ "$CONNECTOR_NAME" == "connector-name" ]; then
    echo "Error: CONNECTOR_NAME environment variable is required but not set."
    echo "Please specify a Confluent Hub connector name (e.g., debezium/debezium-connector-postgresql:2.2.1)"
    exit 1
fi

echo "Downloading connector: $CONNECTOR_NAME"
/opt/confluent/bin/confluent-hub install "$CONNECTOR_NAME" --no-prompt --component-dir=/opt/kafka/plugins
if [ $? -eq 0 ]; then
    echo "Connector $CONNECTOR_NAME installed successfully"
else
    echo "Error: Failed to install connector $CONNECTOR_NAME"
    exit 1
fi
