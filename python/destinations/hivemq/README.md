# HiveMQ

[This connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/hivemq) demonstrates how to consume data from a Kafka topic and publish it to a HiveMQ broker's MQTT topic.

The MQTT topic the example produces to will be `mqtt_topic_root`/`message_key`.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Requirements / Prerequisites

You'll need to have a HiveMQ broker running either locally or in the cloud

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **mqtt_topic_root**: The root for messages in MQTT, this can be anything.

The broker connection comes from the shared **`hivemq-connection`** Variable Group, so this
sink and the HiveMQ Source connect to the same broker with the same credentials:

- **mqtt_server**: Host address of your HiveMQ broker, without the protocol prefix (Required: `True`)
- **mqtt_port**: Port of your HiveMQ broker (Default: `8883`, Required: `True`)
- **mqtt_username**: Username of your HiveMQ user (Required: `False`)
- **mqtt_password**: Password of your HiveMQ user (Required: `False`)
- **mqtt_version**: MQTT protocol version. One of `3.1`, `3.1.1`, `5` (Default: `3.1.1`)
- **mqtt_tls_enabled**: Enable TLS. One of `true`, `false` (Default: `true`, as HiveMQ
  Cloud requires TLS on 8883)

`mqtt_version` and `mqtt_tls_enabled` are free text inside the group rather than
dropdowns - the group schema has no options list. Valid values are given above.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
