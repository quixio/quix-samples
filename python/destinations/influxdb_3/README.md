# InfluxDB v3

[This connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/influxdb_3) demonstrates how to consume data from a Kafka topic in Quix and persist the data to an InfluxDB v3 database using the InfluxDB write API.

To learn more about how it functions, [check out the underlying 
Quix Streams `InfluxDB3Source`](https://quix.io/docs/quix-streams/connectors/sinks/influxdb3-sink.html).

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment Variables

The connector uses the following environment variables:

- **input**: This is the input topic (Default: `detection-result`, Required: `True`)
- **TIMESTAMP_COLUMN**: This is the column in your data that represents the timestamp. Interpreted using `INFLUXDB_TIME_PRECISION`. Defaults to use the message timestamp received from the broker if not supplied. Case sensitive. (Default: ``, Required: `False`)
- **INFLUXDB_TIME_PRECISION**: Precision of the `TIMESTAMP_COLUMN` values. One of `ns`, `us`, `ms`, `s`. (Default: `ns`, Required: `False`)
- **INFLUXDB_TAG_KEYS**: Keys to be used as tags when writing data to InfluxDB. These are columns that are available in the input topic. (Default: ``, Required: `False`)
- **INFLUXDB_FIELD_KEYS**: Keys to be used as fields when writing data to InfluxDB. These are columns that are available in the input topic. (Default: ``, Required: `True`)
- **INFLUXDB_MEASUREMENT_NAME**: The InfluxDB measurement to write data to. If not specified, the name of the input topic will be used. (Default: `measurement1`, Required: `False`)

### Connection (shared `influxdb3-config` variable group)

Connection details come from the shared **`influxdb3-config`** variable group. Assign the same
group to this connector as to the InfluxDB v3 server so the values always match:

- **INFLUXDB3_HOST**: Base URL clients use to reach InfluxDB v3. (Default: `http://influxdb3`, Required: `True`)
- **INFLUXDB3_TOKEN**: InfluxDB v3 admin token, secret. Optional — required only if the server has auth enabled (must start with `apiv3_`); leave blank when the server runs without auth. (Required: `False`)
- **INFLUXDB3_DATABASE**: Default database to write to. (Default: `quix`, Required: `True`)
- **INFLUXDB3_ORG**: Organization id; required by Quix Streams but not used by InfluxDB 3 Core. (Default: `quix`, Required: `False`)

## Requirements / Prerequisites

You will need an InfluxDB 3.0 instance available. When paired with the Quix **InfluxDB v3** server
sample, deploy that first and assign it the same `influxdb3-config` variable group.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
