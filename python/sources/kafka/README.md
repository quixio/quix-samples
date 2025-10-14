# Kafka Replicator Source

This source template replicates data from a Kafka topic to a Quix topic using the `KafkaReplicatorSource` class from Quix Streams.

## Features

- Replicates data from any Kafka broker to Quix
- Supports SASL/SSL authentication
- Configurable deserializers for keys and values
- Configurable consumer behavior (offset reset, poll timeout, etc.)
- Support for running multiple instances with the same name

## Environment Variables

### Required

- **output**: The Quix topic that will receive the replicated data
- **SOURCE_BROKER_ADDRESS**: The source Kafka broker address (e.g., `localhost:9092` or `broker.example.com:9092`)
- **SOURCE_TOPIC**: The source Kafka topic name to replicate from

### Optional

- **AUTO_OFFSET_RESET**: What to do when there is no initial offset in Kafka. Options: `earliest`, `latest`. Default: `latest`
- **VALUE_DESERIALIZER**: Deserializer to use for the message value. Options: `json`, `bytes`, `string`, `double`, `integer`. Default: `json`
- **KEY_DESERIALIZER**: Deserializer to use for the message key. Options: `json`, `bytes`, `string`, `double`, `integer`. Default: `bytes`
- **CONSUMER_POLL_TIMEOUT**: Consumer poll timeout in seconds (optional)
- **SHUTDOWN_TIMEOUT**: Timeout for shutting down the source in seconds. Default: `10`

### Authentication (Optional)

If your source Kafka cluster requires authentication, provide these variables:

- **SOURCE_KAFKA_SASL_USERNAME**: SASL username for source Kafka authentication
- **SOURCE_KAFKA_SASL_PASSWORD**: SASL password for source Kafka authentication
- **SOURCE_KAFKA_SASL_MECHANISM**: SASL mechanism for authentication. Options: `PLAIN`, `SCRAM-SHA-256`, `SCRAM-SHA-512`, `GSSAPI`, `OAUTHBEARER`, `AWS_MSK_IAM`. Default: `SCRAM-SHA-256`
- **SOURCE_KAFKA_SSL_CA_LOCATION**: Path to the SSL CA certificate file for secure connections

## How It Works

1. The template creates a connection to the source Kafka broker using the provided configuration
2. It uses the `KafkaReplicatorSource` to consume messages from the source topic
3. Messages are automatically replicated to the output topic in Quix
4. The replication preserves message keys, values, and metadata

## Use Cases

- Migrating data from one Kafka cluster to another
- Creating a real-time backup of a Kafka topic
- Integrating external Kafka data sources into Quix pipelines
- Bridging data between different Kafka environments (e.g., on-premise to cloud)

## Example Configuration

For a public Kafka broker without authentication:
```
SOURCE_BROKER_ADDRESS=localhost:9092
SOURCE_TOPIC=my-source-topic
output=replicated-data
```

For a secured Kafka cluster:
```
SOURCE_BROKER_ADDRESS=broker.example.com:9092
SOURCE_TOPIC=my-source-topic
output=replicated-data
SOURCE_KAFKA_SASL_USERNAME=my-username
SOURCE_KAFKA_SASL_PASSWORD=my-password
SOURCE_KAFKA_SASL_MECHANISM=SCRAM-SHA-256
```

## Notes

- The `KafkaReplicatorSource` supports running multiple instances with the same name for parallel processing
- If no authentication variables are provided, the connector will attempt to connect without SASL/SSL
- Make sure the source Kafka broker is accessible from the Quix environment