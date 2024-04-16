# Kafka Connect Sink

[This sample code](https://github.com/quixio/quix-samples/tree/main/shell/kafka-connect-sink) shows you how to install any Kafka Connect sink connector using its Confluent Hub name.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

After forking the project, a file at the root directory named `connector.properties` should be filled with your connector configuration before being deployed.

## Environment variables

The code sample uses the following environment variables:

- **input**: The name of the input topic to sink data from.
- **CONNECT_OFFSET_STORAGE_TOPIC**: Topic name to use for storing offsets for Kafka Connect.
- **CONNECT_CONFIG_STORAGE_TOPIC**: Topic name to use for storing connector and task configurations for Kafka Connect.
- **CONNECT_STATUS_STORAGE_TOPIC**: Topic name to use for storing statuses for Kafka Connect.
- **CONNECTOR_NAME**: The [Confluent Hub](https://www.confluent.io/hub) Kafka connector to use ("Free" licence connectors only for now). Example: `snowflakeinc/snowflake-kafka-connector:2.1.2`.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
