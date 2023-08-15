

# InfluxDB-3.0 Destination Plugin

## Introduction

The InfluxDB-3.0 destination plugin allows you to publish Quix streams to InfluxDB 3.0. It's written in Python and is designed to be both easy to use and versatile.

## Requirements

To set up and run the InfluxDB-3.0 destination plugin, you need the following dependencies:
```
quixstreams==0.5.2
influxdb3-python
pandas
```

## Configuration Details

To configure the InfluxDB-3.0 destination plugin, you'll need to set up the following variables:

- **input**: This is the input topic (Default: `detection-result`, Required: `True`)
- **INFLUXDB_HOST**: Host address for the InfluxDB instance. (Default: `eu-central-1-1.aws.cloud2.influxdata.com`, Required: `True`)
- **INFLUXDB_TOKEN**: Authentication token to access InfluxDB. (Default: `<TOKEN>`, Required: `True`)
- **INFLUXDB_ORG**: Organization name in InfluxDB. (Default: `<ORG>`, Required: `False`)
- **INFLUXDB_DATABASE**: Database name in InfluxDB where data should be stored. (Default: `<DATABASE>`, Required: `True`)
- **INFLUXDB_TAG_COLUMNS**: Columns to be used as tags when writing data to InfluxDB. (Default: `['tag1', 'tag2']`, Required: `False`)
- **INFLUXDB_MEASUREMENT_NAME**: The InfluxDB measurment to write data to. If not specified, the name of the input topic will be used. (Default: `<INSERT MEASUREMENT>`, Required: `False`)


## Setup and Usage

1. Ensure you have all the required dependencies installed.
2. Configure the necessary variables as mentioned above.
3. Use the provided `main.py` as the entry point for the plugin.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.

