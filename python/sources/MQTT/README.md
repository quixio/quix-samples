# MQTT

[This connector](https://github.com/quixio/quix-samples/tree/main/python/sources/MQTT) demonstrates how to consume data from an MQTT broker and publish that data to a Kafka topic.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment Variables

The connector uses the following environment variables:

- **output**: Name of the output topic to publish to.
- **mqtt_topic**: The MQTT topic to listen to. Can use wildcards e.g. MyTopic/#
- **mqtt_server**: The address of your MQTT server.
- **mqtt_port**: The port of your MQTT server.
- **mqtt_username**: Username of your MQTT user.
- **mqtt_password**: Password for the MQTT user.

## Requirements / Prerequisites

You'll need to have a MQTT broker either locally or in the cloud

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
