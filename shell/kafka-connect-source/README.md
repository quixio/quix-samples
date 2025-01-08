# Kafka Connect Source

[This connector](https://github.com/quixio/quix-samples/tree/main/shell/kafka-connect-source) shows you how to install any Kafka Connect source connector using its Confluent Hub name.

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

After saving the project, a file at the root directory named `connector.properties` should be filled with your connector configuration before being deployed.

## Environment variables

The connector uses the following environment variables:

- **output**: The name of the output topic to publish the sourced data to.
- **CONNECT_OFFSET_STORAGE_TOPIC**: Topic name to use for storing offsets for Kafka Connect.
- **CONNECT_CONFIG_STORAGE_TOPIC**: Topic name to use for storing connector and task configurations for Kafka Connect.
- **CONNECT_STATUS_STORAGE_TOPIC**: Topic name to use for storing statuses for Kafka Connect.
- **CONNECTOR_NAME**: The [Confluent Hub](https://www.confluent.io/hub) Kafka connector to use ("Free" licence connectors only for now). Example: `debezium/debezium-connector-postgresql:2.2.1`.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
