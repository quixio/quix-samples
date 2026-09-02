# Confluent Kafka

[This connector](https://github.com/quixio/quix-samples/tree/main/python/sources/confluent_kafka) demonstrates how to consume data from a Kafka topic in Confluent Cloud and publish the data to a Kafka topic configured in Quix.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment variables

The connector uses the following environment variables:

- **output**: This is the Quix Topic that will receive the stream.
- **kafka_topic**: The Confluent Kafka Topic you wish to read from.
- **kafka_ca_location**: (Optional) Path to the SSL CA certificate file for secure connections. If not provided, the system's default CA certificates will be used.
- **kafka_sasl_mechanism**: (Optional) SASL mechanism for authentication. Defaults to "SCRAM-SHA-256".

The cluster connection comes from the shared **`confluent-kafka-connection`** Variable Group,
so this source and the Confluent Kafka Sink talk to the same cluster with the same API key:

- **kafka_broker_address**: Bootstrap server address, obtained from the Confluent Kafka portal (Required: `True`)
- **kafka_key**: API key, obtained from the Confluent Kafka portal (Required: `True`)
- **kafka_secret**: API secret, obtained from the Confluent Kafka portal (Required: `True`)
- **kafka_sasl_mechanism**: SASL mechanism. One of `PLAIN`, `SCRAM-SHA-256`,
  `SCRAM-SHA-512`, `GSSAPI`, `OAUTHBEARER`, `AWS_MSK_IAM` (Default: `PLAIN`, which is what
  Confluent Cloud API keys use)
- **kafka_ca_location**: Path to the SSL CA certificate file. Leave empty for the system
  defaults

Note that the group default for `kafka_sasl_mechanism` is `PLAIN`, whereas this source used
to default to `SCRAM-SHA-256`. Existing deployments carry their own value and are
unaffected; a fresh deployment using the group will authenticate with `PLAIN` unless you
change it.

`kafka_sasl_mechanism` is free text inside the group rather than a dropdown - the
group schema has no options list. Valid values are given above.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
