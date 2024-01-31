#!/usr/bin/env bash

if [ -z "$CONNECTOR_NAME" ] || [ "$CONNECTOR_NAME" == "connector-name" ]; then
    echo "Error: Environment variable CONNECTOR_NAME is not set."
    exit 1
fi
    
/opt/confluent/bin/confluent-hub install "$CONNECTOR_NAME" --no-prompt --component-dir=/opt/kafka/plugins; exit 0
