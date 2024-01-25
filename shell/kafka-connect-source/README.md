# Kafka Connect Source

[This project](https://github.com/quixio/quix-samples/tree/main/shell/kafka-connect-source) shows you how to install a kafka connect source connector.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **output**: This is the output topic for VisualCrossing data.
- **CONNECT_OFFSET_STORAGE_TOPIC**: Topic name to use for storing kafka connect offsets
- **CONNECT_CONFIG_STORAGE_TOPIC**: Topic name to use for storing connector and task configurations for kafka connect
- **CONNECT_STATUS_STORAGE_TOPIC**: Topic name to use for storing statuses for kafka connect
- **CONNECTOR_NAME**: The [confluent hub](https://www.confluent.io/hub) (free connectors only for now) kafka connector to use. Example: `jcustenborder/kafka-connect-redis:0.0.5`

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

