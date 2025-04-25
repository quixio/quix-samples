# InfluxDB v3

[This connector](https://github.com/quixio/quix-samples/tree/main/python/sources/influxdb_3) demonstrates how to use the InfluxDB v3 query API to periodically 
query InfluxDB3 and publish the results to a Kafka topic.

To learn more about how it functions, [check out the underlying 
Quix Streams `InfluxDB3Source`](https://quix.io/docs/quix-streams/connectors/sources/influxdb3-source.html).

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment Variables

The connector uses the following environment variables:

### Required

- `output`: The Kafka topic that will receive the query results.
- `INFLUXDB_HOST`: Host address for the InfluxDB instance.
- `INFLUXDB_TOKEN`: Authentication token to access InfluxDB.
- `INFLUXDB_ORG`: Organization name in InfluxDB.
- `INFLUXDB_DATABASE`: Database name in InfluxDB where data is stored.

### Optional

- `INFLUXDB_QUERY_MEASUREMENTS`: The measurements to query. If left None, all measurements will be processed.
- `INFLUXDB_RECORD_TIMESTAMP_COLUMN`: The InfluxDB record column used for the Kafka timestamp, else uses Kafka default (produce time).
- `INFLUXDB_RECORD_MEASUREMENT_COLUMN`: The column name used for inserting the measurement name, else uses `'_measurement'`. 
- `INFLUXDB_QUERY_SQL`: A custom SQL query to use for retrieving data from InfluxDB, else uses default.
- `INFLUXDB_QUERY_START_DATE`: The RFC3339-formatted start time for querying InfluxDB, else uses current runtime.
- `INFLUXDB_QUERY_END_DATE`: The RFC3339-formatted end time for querying InfluxDB, else runs indefinitely for 1 measurement only.
- `INFLUXDB_QUERY_TIME_DELTA`: Time interval for batching queries, e.g., `'5m'` for 5 minutes.
- `INFLUXDB_QUERY_MAX_RETRIES`: Maximum number of retries for querying or producing (with multiplicative backoff).
- `INFLUXDB_QUERY_DELAY_SECONDS`: Add an optional delay (in seconds) between producing batches
- `CONSUMER_GROUP_NAME`: The name of the consumer group to use when consuming from Kafka.
- `BUFFER_SIZE`: The number of records that sink holds before flush data to InfluxDb.
- `BUFFER_TIMEOUT`: The number of seconds that sink holds before flush data to the InfluxDb.

## Requirements / Prerequisites

You will need to have an InfluxDB 3.0 instance available and an API authentication token (
unless otherwise noted).

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
