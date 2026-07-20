# InfluxDB v3

[This connector](https://github.com/quixio/quix-samples/tree/main/python/sources/influxdb_3) demonstrates how to use the InfluxDB v3 query API to periodically query InfluxDB and publish the results to a Kafka topic.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment Variables

The connector uses the following environment variables:

- **output**: This is the output topic that will receive the stream (Default: `influxdb`, Required: `True`)
- **task_interval**: Interval to run query. Must be within the InfluxDB notation; 1s, 1m, 1h, 1d, 1w, 1mo, 1y (Default: `5m`, Required: `True`)
- **INFLUXDB_MEASUREMENT_NAME**: The InfluxDB measurement to read data from. If not specified, the name of the output topic will be used (Default: `<INSERT MEASUREMENT>`, Required: `False`)

### Connection (shared `influxdb3-config` variable group)

Connection details come from the shared **`influxdb3-config`** variable group. Assign the same
group to this connector as to the InfluxDB v3 server so the values always match:

- **INFLUXDB3_HOST**: Base URL clients use to reach InfluxDB v3. (Default: `http://influxdb3`, Required: `True`)
- **INFLUXDB3_USE_TOKEN**: Whether the InfluxDB v3 server has authentication enabled. (Default: `false`, Required: `True`)
- **INFLUXDB3_TOKEN**: InfluxDB v3 admin token, secret. Used only when `INFLUXDB3_USE_TOKEN` is `true` (must start with `apiv3_`). (Default: `CHANGE_ME`, Required: `True`)
- **INFLUXDB3_DATABASE**: Default database to read from. (Default: `quix`, Required: `True`)
- **INFLUXDB3_ORG**: Organization id; required by Quix Streams but not used by InfluxDB 3 Core. (Default: `quix`, Required: `False`)

## Requirements / Prerequisites

You will need an InfluxDB 3.0 instance available. When paired with the Quix **InfluxDB v3** server
sample, deploy that first and assign it the same `influxdb3-config` variable group.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
