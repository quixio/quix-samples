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

The broker connection comes from the shared **`mqtt-connection`** Variable Group, so this
source, the MQTT Sink and the bundled Mosquitto broker all agree:

- **mqtt_server**: Host address of your MQTT broker, without the protocol prefix (Default: `mqtt`)
- **mqtt_port**: Port of your MQTT broker (Default: `1883`)
- **mqtt_username**: Username to connect to the broker with (Default: `admin`)
- **mqtt_password**: Password to connect to the broker with
- **mqtt_version**: MQTT protocol version. One of `3.1`, `3.1.1`, `5` (Default: `3.1.1`)
- **mqtt_tls_enabled**: Enable TLS. One of `true`, `false` (Default: `false`, since the
  bundled Mosquitto broker listens plaintext on 1883)

`mqtt_version` and `mqtt_tls_enabled` are free text inside the group rather than
dropdowns - the group schema has no options list. Valid values are given above.

## Requirements / Prerequisites

You'll need to have an MQTT broker either locally or in the cloud

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
