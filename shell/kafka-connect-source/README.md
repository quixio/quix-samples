# Kafka Connect Source

[This connector](https://github.com/quixio/quix-samples/tree/main/shell/kafka-connect-source) shows you how to install any Kafka Connect source connector using its Confluent Hub name.

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log-in and visit the `Connectors` tab to use this connector.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise` (above variables) to inspect or alter the code before deployment.

After saving the project, a file at the root directory named `connector.properties` should be filled with your connector configuration before being deployed.

## SSL/TLS Configuration

The connector automatically handles SSL/TLS connections:
- If custom CA certificates are provided by Quix, they will be used for SSL connections
- If no custom certificates are available, the system's default trusted CAs (e.g., Let's Encrypt) will be used
- The connector supports PLAINTEXT, SSL, SASL_PLAINTEXT, and SASL_SSL security protocols

## Environment variables

The connector uses the following environment variables:

- **output**: The name of the output topic to publish the sourced data to.
- **CONNECT_OFFSET_STORAGE_TOPIC**: Topic name to use for storing offsets for Kafka Connect.
- **CONNECT_CONFIG_STORAGE_TOPIC**: Topic name to use for storing connector and task configurations for Kafka Connect.
- **CONNECT_STATUS_STORAGE_TOPIC**: Topic name to use for storing statuses for Kafka Connect.
- **CONNECTOR_NAME**: **(Required)** The [Confluent Hub](https://www.confluent.io/hub) Kafka connector to use ("Free" licence connectors only). Example: `debezium/debezium-connector-postgresql:2.2.1`.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
