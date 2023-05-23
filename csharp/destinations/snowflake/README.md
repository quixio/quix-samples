# Snowflake

[This project](https://github.com/quixio/quix-samples/tree/main/csharp/destinations/snowflake) allows the user to publish data from Quix to Snowflake, it handles both parameter and event data.

Once connected to your existing SnowFlake database, this connector will create and populate tables for:

 - **Event values** - The individual event values from the streamed data.
 - **Events details** - The event ID, name, originating stream, location, level, etc.
 - **Event groups** - Event group details.
 - **Parameter values** - The individual parameter data values from the streamed data.
 - **Parameter details** - The parameter ID, name, originating stream, min and max values, etc.
 - **Parameter groups** - Parameter group details.
 - **Streams** - Details regarding which streams have contributed to the stored data.
 - **Stream metadata** - Metadata for each stream that has contributed to the stored data.
 - **Stream parents** - Parents of the streams that have contributed to the stored data. 

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Setup & deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **Broker__TopicName**: Name of the Quix topic to source data from.
- **Snowflake__Locator**: Locator of the account. Can be found under Admin/Accounts or in the URL. Note that the locator will be similar to this `vz12303`.
  - **note**: The url has the format: `https://app.snowflake.com/{region}/locator`
- **Snowflake__Region**: Region of the account. Can be found in the URL after `https://app.snowflake.com/`.
  - e.g.: `west-europe.azure` this is highly dependent on the cloud provider you chose for your Snowflake account. 
  - **note**: The url has the format: `https://app.snowflake.com/{region}/locator`
- **Snowflake__Database**: The name of the database to persist to. 
  - **note**: you must create this database. The Quix Snowflake connector will create and populate the tables.
- **Snowflake__User**: The username of the user the sink should use to interact with the database.
- **Snowflake__Password**: The password of the user configured above.

## Requirements / Prerequisites
 - A Snowflake account.

## Known limitations 
- Binary parameters are not supported in this version

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

