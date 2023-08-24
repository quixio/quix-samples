# InfluxDB 3.0

Read data from InfluxDB 3.0 with [this project](https://github.com/quixio/quix-samples/tree/main/python/sources/InfluxDB).

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Configuration Details

To configure the InfluxDB-3.0 destination plugin, you'll need to set up the following variables:

- **output**: This is the Quix Topic that will receive the stream (Default: `influxdb`, Required: `True`)
- **task_interval**: Interval to run query. Must be within the InfluxDB notation; 1s, 1m, 1h, 1d, 1w, 1mo, 1y (Default: `5m`, Required: `True`)
- **INFLUXDB_HOST**: Host address for the InfluxDB instance. (Default: `eu-central-1-1.aws.cloud2.influxdata.com`, Required: `True`)
- **INFLUXDB_TOKEN**: Authentication token to access InfluxDB. (Default: `<TOKEN>`, Required: `True`)
- **INFLUXDB_ORG**: Organization name in InfluxDB. (Default: `<ORG>`, Required: `False`)
- **INFLUXDB_DATABASE**: Database name in InfluxDB where data should be stored. (Default: `<DATABASE>`, Required: `True`)
- **INFLUXDB_MEASUREMENT_NAME**: The InfluxDB measurment to write data to. If not specified, the name of the input topic will be used (Default: `<INSERT MEASUREMENT>`, Required: `False`)


## Setup and Usage

1. Ensure you have all the required dependencies installed.
2. Configure the necessary variables as mentioned above.
3. Use the provided `main.py` as the entry point for the plugin.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.

