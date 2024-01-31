#!/bin/bash -e

sh /usr/bin/download-connector.sh

# Start by updating the bootstrap servers in the configuration file
sh /usr/bin/update-bootstrapservers.sh

# Standalone mode
#exec "/opt/kafka/bin/connect-distributed.sh" "/opt/kafka/config/connect-standalone.properties"

# Distributed mode
#exec "/opt/kafka/bin/connect-distributed.sh" "/opt/kafka/config/connect-distributed.properties" 

if [ -z "$CONNECT_MODE" ] || [ "$CONNECT_MODE" == "standalone" ]; then
    exec "/opt/kafka/bin/connect-standalone.sh" "/opt/kafka/config/connect-standalone.properties" "/opt/kafka/config/connector.properties"
else
    exec "/opt/kafka/bin/connect-distributed.sh" "/opt/kafka/config/connect-distributed.properties" "/opt/kafka/config/connector.properties"
fi

#   If you want to automatically start the connector, the connector propertries file must be passed as a second argument.
#   Otherwise, you can configure the connector manually using the REST API.
# 
#   Example:
#   PUT http://localhost:8083/connectors/myconnector/config
#   {
#     "name": "rabbitmq-source-connector",
#     "tasks.max": "10",
#     "connector.class": "io.confluent.connect.rabbitmq.RabbitMQSourceConnector",
#     "rabbitmq.host": "rabbitmq",
#     "rabbitmq.port": "5672",
#     "rabbitmq.username": "guest",
#     "rabbitmq.password": "guest",
#     "rabbitmq.virtual.host": "/",
#     "rabbitmq.prefetch.count": "500",
#     "rabbitmq.automatic.recovery.enabled": "true",
#     "rabbitmq.network.recovery.interval.ms": "10000",
#     "rabbitmq.topology.recovery.enabled": "true",
#     "kafka.topic": "rabbitmq.test",
#     "rabbitmq.queue": "test",
#     "confluent.topic.bootstrap.servers": "broker-1:29091"
#    }