# InfluxDB 2.0

Periodically query InfluxDB 2.0 and publish the results to a Kafka topic using [this sample code](https://github.com/quixio/quix-samples/tree/develop/python/sources/influxdb_2).

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log in and visit the Code Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment Variables

The code sample uses the following environment variables:

- **output**: This is the ouput topic that will receive the stream (Default: `influxdb`, Required: `True`)
- **task_interval**: Interval to run query. Must be within the InfluxDB notation; 1s, 1m, 1h, 1d, 1w, 1mo, 1y (Default: `5m`, Required: `True`)
- **INFLUXDB_HOST**: Host address for the InfluxDB instance. (Default: `eu-central-1-1.aws.cloud2.influxdata.com`, Required: `True`)
- **INFLUXDB_TOKEN**: Authentication token to access InfluxDB. (Default: `<TOKEN>`, Required: `True`)
- **INFLUXDB_ORG**: Organization name in InfluxDB. (Default: `<ORG>`, Required: `False`)
- **INFLUXDB_BUCKET**: Bucket name in InfluxDB where data is stored. (Default: `<BUCKET>`, Required: `True`)
- **INFLUXDB_MEASUREMENT_NAME**: The InfluxDB measurement to read data from. If not specified, the name of the output topic will be used (Default: `<INSERT MEASUREMENT>`, Required: `False`)

## Requirements / Prerequisites

You will need to have an InfluxDB 2.0 instance available and an API authentication token.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
