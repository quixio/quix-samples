# TDengine

[This connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/tdengine) demonstrates how to consume data from a Kafka topic in Quix and persist the data to an TDengine database using the TDengine write API.

To learn more about how it functions, [check out the underlying 
Quix Streams `TDengine3Sink`](https://quix.io/docs/quix-streams/connectors/sinks/tdengine-sink.html).

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment Variables

The connector uses the following environment variables:

- **input**: This is the input topic (Default: `detection-result`, Required: `True`)
- **TDENGINE_HOST**: Host address for the TDengine instance. (Required: `True`)
- **TDENGINE_TOKEN**: Authentication token to access TDengine. (Required: `True`)
- **TDENGINE_DATABASE**: Database name in TDengine where data should be stored. (Required: `True`)
- **TDENGINE_SUPERTABLE**: Supertable name in TDengine. (Required: `True`)
- **TIMESTAMP_COLUMN**: This is the column in your data that represents the timestamp in nanoseconds. Defaults to use the message timestamp received from the broker if not supplied. Case sensitive. (Default: ``, Required: `False`)
- **TDENGINE_TAG_KEYS**: Keys to be used as tags when writing data to TDengine. These are columns that are available in the input topic. (Default: ``, Required: `False`)
- **TDENGINE_FIELD_KEYS**: Keys to be used as fields when writing data to TDengine. These are columns that are available in the input topic. (Default: ``, Required: `True`)

## Requirements / Prerequisites

You will need to have an TDengine instance available and an API authentication token.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
