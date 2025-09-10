# MQTT

[This connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/MQTT) demonstrates how to produce data from a Kafka topic and publish it to an MQTT broker.

The MQTT topic the example produces to will be `mqtt_topic_root`/`message_key`.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Requirements / Prerequisites

You'll need to have an MQTT broker either locally or in the cloud

## Environment Variables

The connector uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **MQTT_CLIENT_ID**: A client ID for the sink.  
  **Default**: `mqtt-sink`
- **MQTT_TOPIC_ROOT**: The root for messages in MQTT, this can be anything.
- **MQTT_SERVER**: The address of your MQTT server.
- **MQTT_PORT**: The port of your MQTT server.  
  **Default**: `8883`
- **MQTT_USERNAME**: Username of your MQTT user.
- **MQTT_PASSWORD**: Password for the MQTT user.
- **MQTT_VERSION**: MQTT protocol version; choose 3.1, 3.1.1, or 5.  
  **Default**: `3.1.1`
- **MQTT_USE_TLS**: Set to true if the server uses TLS.  
  **Default**: `True`

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
