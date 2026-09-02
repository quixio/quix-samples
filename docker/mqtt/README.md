# MQTT (Mosquitto)

This sample demonstrates how to deploy and use Mosquitto's MQTT server in your pipeline. Please note: this image is provided by Mosquitto and is offered as-is, with no specific support from Quix.

## Using with a Quix Cloud MQTT Connector

This deployment will work seamlessly with the [Quix Cloud MQTT sink connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/mqtt).

Assign the same `mqtt-connection` variable group to the connector and it picks up the
matching address and credentials automatically - no need to copy the values by hand:

```shell
mqtt_server="mqtt"      # the internal service name
mqtt_port="1883"
mqtt_username="admin"
mqtt_password="<YOUR PASSWORD>"
```

## Configuration

This sample uses the shared **`mqtt-connection`** variable group, so the broker and every
client (source/sink) read the same address and credentials. Assign the group to this
deployment (or your project/environment) with:

- **mqtt_server** — host address clients use to reach the broker (default `mqtt`, the internal service name)
- **mqtt_port** — port clients connect on (default `1883`)
- **mqtt_username** — username the broker is seeded with, and that clients authenticate as (default `admin`)
- **mqtt_password** — password for that user, secret

`mosquitto.conf` sets `allow_anonymous false`, so both a username and a password are
required and the container exits with an error if either is empty. The legacy
`MQTT_USERNAME` / `MQTT_PASSWORD` variables still work for deployments created before the
group was introduced.

## How to Run

1. Log in or sign up at [Quix](https://portal.platform.quix.io/signup?xlink=github) and navigate to the Code Samples section.
2. Click **Deploy** to launch a pre-built container.
3. Assign the `mqtt-connection` variable group, setting at least `mqtt_password`.
4. Enable state, otherwise changes will be lost on restart. Please note, the necessary storage type may not be supported on all Quix Platforms.

For more configuration options and details, refer to [Mosquitto Docker Hub](https://hub.docker.com/_/eclipse-mosquitto).


## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by the [docker community](https://github.com/docker-library/mongo) and is offered as-is, with no MongoDB specific support from Quix.
