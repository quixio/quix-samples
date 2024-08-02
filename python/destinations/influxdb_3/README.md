# InfluxDB 3.0

[This code sample](https://github.com/quixio/quix-samples/tree/develop/python/destinations/influxdb_3) demonstrates how to consume data from a Kafka topic in Quix and persist the data to an InfluxDB 3.0 database using the InfluxDB write API.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log in and visit the Code Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment Variables

The code sample uses the following environment variables:

- **input**: This is the input topic (Default: `detection-result`, Required: `True`)
- **TIMESTAMP_COLUMN**: This is the column in your data that represents the timestamp in nanoseconds. Defaults to use the message timestamp received from the broker if not supplied. Case sensitive. (Default: ``, Required: `False`)
- **INFLUXDB_HOST**: Host address for the InfluxDB instance. (Default: `https://eu-central-1-1.aws.cloud2.influxdata.com`, Required: `True`)
- **INFLUXDB_TOKEN**: Authentication token to access InfluxDB. (Default: `<TOKEN>`, Required: `True`)
- **INFLUXDB_ORG**: Organization name in InfluxDB. (Default: `<ORG>`, Required: `False`)
- **INFLUXDB_DATABASE**: Database name in InfluxDB where data should be stored. (Default: `<DATABASE>`, Required: `True`)
- **INFLUXDB_TAG_KEYS**: Keys to be used as tags when writing data to InfluxDB. These are columns that are available in the input topic. (Default: ``, Required: `False`)
- **INFLUXDB_FIELD_KEYS**: Keys to be used as fields when writing data to InfluxDB. These are columns that are available in the input topic. (Default: ``, Required: `True`)
- **INFLUXDB_MEASUREMENT_NAME**: The InfluxDB measurement to write data to. If not specified, the name of the input topic will be used. (Default: `measurement1`, Required: `False`)

## Requirements / Prerequisites

You will need to have an InfluxDB 3.0 instance available and an API authentication token.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
