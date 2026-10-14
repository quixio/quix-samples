# Confluent Kafka

[This connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/confluent_kafka) demonstrates how to consume data from a Kafka topic in Quix and publish it to a topic in Confluent Cloud.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment variables

The connector uses the following environment variables:

- **input**: This is the Quix topic to listen to.
- **kafka_topic**: The Confluent Kafka Topic you wish to read from.

The cluster connection comes from the shared **`confluent-kafka-connection`** Variable Group,
so this sink and the Confluent Kafka Source talk to the same cluster with the same API key:

- **kafka_broker_address**: Bootstrap server address, obtained from the Confluent Kafka portal (Required: `True`)
- **kafka_key**: API key, obtained from the Confluent Kafka portal (Required: `True`)
- **kafka_secret**: API secret, obtained from the Confluent Kafka portal (Required: `True`)
- **kafka_sasl_mechanism**: SASL mechanism. One of `PLAIN`, `SCRAM-SHA-256`,
  `SCRAM-SHA-512`, `GSSAPI`, `OAUTHBEARER`, `AWS_MSK_IAM` (Default: `PLAIN`)
- **kafka_ca_location**: Path to the SSL CA certificate file. Leave empty for the system
  defaults

This sink previously hard-coded `PLAIN` and ignored any CA path, so it could not reach a
SCRAM-authenticated cluster that the Confluent Kafka Source could. It now reads both from
the group, so the two ends authenticate the same way.

`kafka_sasl_mechanism` is free text inside the group rather than a dropdown - the
group schema has no options list. Valid values are given above.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
