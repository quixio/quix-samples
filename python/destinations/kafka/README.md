# Kafka Replicator Sink

[This connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/kafka) demonstrates how to consume data from a Quix topic and produce it to an external Kafka cluster.

This sink uses the `KafkaReplicatorSink` to serialize and produce messages to an external Kafka cluster, making it easy to replicate data between Kafka clusters or export data from Quix to other Kafka-based systems.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either:
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix.

* or click `Customise connector` to inspect or alter the code before deployment.

## Requirements / Prerequisites

You'll need to have an external Kafka cluster accessible either locally or in the cloud.

## Environment Variables

The connector uses the following environment variables:

### Required
- **input**: Name of the input topic to listen to.
- **SINK_OUTPUT_TOPIC**: The target Kafka topic name to produce to on the external Kafka cluster.
- **SINK_BOOTSTRAP_SERVERS**: The external Kafka broker address (e.g., localhost:9092 or broker.example.com:9092).

### Optional
- **CONSUMER_GROUP**: Name of the consumer group for consuming from Quix. Default: "kafka_sink"
- **SINK_KEY_SERIALIZER**: Serializer to use for the message key. Options: json, bytes, string, double, integer. Default: "bytes"
- **SINK_VALUE_SERIALIZER**: Serializer to use for the message value. Options: json, bytes, string, double, integer. Default: "json"
- **SINK_AUTO_CREATE_TOPIC**: Whether to attempt to create the sink topic upon startup. Default: "true"

### Authentication (Optional)
- **SINK_SECURITY_PROTOCOL**: Protocol used to communicate with brokers. Options: PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL
- **SINK_SASL_MECHANISM**: SASL mechanism for authentication. Options: PLAIN, SCRAM-SHA-256, SCRAM-SHA-512, GSSAPI, OAUTHBEARER, AWS_MSK_IAM
- **SINK_SASL_USERNAME**: SASL username for external Kafka authentication.
- **SINK_SASL_PASSWORD**: SASL password for external Kafka authentication.
- **SINK_SSL_CA_LOCATION**: Path to the SSL CA certificate file for secure connections.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
