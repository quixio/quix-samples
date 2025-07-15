# InfluxDB v1

[This connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/influxdb_1) demonstrates how to 
consume data from a Kafka topic in Quix and persist the data to an InfluxDB v3 database using the InfluxDB v1 write API.

To learn more about how it functions, [check out the underlying 
Quix Streams `InfluxDB1Source`](https://quix.io/docs/quix-streams/connectors/sinks/influxdb1-sink.html).

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment Variables

The connector uses the following environment variables:

### Required
- **input**: Quix input topic
- **INFLUXDB_HOST**: Host address for the InfluxDB instance.
- **INFLUXDB_PORT**: Port for the InfluxDB instance.
- **INFLUXDB_USERNAME**: Username for the InfluxDB instance.
- **INFLUXDB_PASSWORD**: Password for the InfluxDB instance.

### Optional
- **INFLUXDB_DATABASE**: Database name in InfluxDB where data should be stored. 
  Default: `quix`
- **INFLUXDB_TAG_KEYS**: A comma-separated list of column names (based on message value) to be used as tags when writing data to InfluxDB.
  Can optionally replace with a callable in the template directly.
- **INFLUXDB_FIELD_KEYS**: A comma-separated list of column names (based on message value) to be used as fields when writing data to InfluxDB.
  Can optionally replace with a callable in the template directly.
- **INFLUXDB_MEASUREMENT_NAME**: The InfluxDB measurement to write data to. 
  Can optionally replace with a callable in the template directly.
  Default: `default`
- **TIMESTAMP_COLUMN**: This is the column in your data that represents the timestamp in nanoseconds. 
  Defaults to use the message timestamp received from the broker if not supplied.
  Can optionally replace with a callable in the template directly.
- **BUFFER_SIZE**: Number of records to buffer before writing to TDengine.  
  Default: `50`
- **BUFFER_TIMEOUT**: Maximum time (in seconds) to buffer records before writing to TDengine.  
  Default: `1`

## Requirements / Prerequisites

You will need to have an InfluxDB 3.0 instance available and an API authentication token.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
