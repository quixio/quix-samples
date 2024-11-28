# HiveMQ

[This code sample](https://github.com/quixio/quix-samples/tree/main/python/destinations/hivemq) demonstrates how to consume data from a Kafka topic and publish it to a HiveMQ broker's MQTT topic.

The MQTT topic the example produces to will be `mqtt_topic_root`/`message_key`.

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log in and visit the Connectors to use this project.

Clicking `Deploy` on the connector, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Requirements / Prerequisites

You'll need to have a MQTT either locally or in the cloud

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **mqtt_topic_root**: The root for messages in MQTT, this can be anything.
- **mqtt_server**: The address of your MQTT server.
- **mqtt_port**: The port of your MQTT server.
- **mqtt_username**: Username of your MQTT user.
- **mqtt_password**: Password for the MQTT user.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
