# PostgreSQL Sink

[This code sample](https://github.com/quixio/quix-samples/tree/main/python/destinations/postgresql_sink) demonstrates how to consume data from a Kafka topic in Quix and persist the data to a PostgreSQL database using the `PostgresSink`.

## How to Run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log in and visit the Code Samples to use this project.

Clicking `Deploy` on the Sample deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample forks the project to your own Git repo so you can customize it before deploying.

## Environment Variables

The code sample uses the following environment variables:

- **input**: This is the input topic (Default: `detection-result`, Required: `True`)
- **POSTGRES_HOST**: Host address for the PostgreSQL instance. (Default: `localhost`, Required: `True`)
- **POSTGRES_PORT**: Port number for the PostgreSQL instance. (Default: `5432`, Required: `True`)
- **POSTGRES_DBNAME**: Database name in PostgreSQL where data should be stored. (Default: `mydatabase`, Required: `True`)
- **POSTGRES_USER**: Username for the PostgreSQL database. (Default: `myuser`, Required: `True`)
- **POSTGRES_PASSWORD**: Password for the PostgreSQL database. (Default: `mypassword`, Required: `True`)
- **POSTGRES_TABLE**: The PostgreSQL table where data will be stored. If the table does not exist, it will be created automatically. (Default: `numbers`, Required: `True`)
- **SCHEMA_AUTO_UPDATE**: Automatically update the schema by adding new columns when new fields are detected. (Default: `true`, Required: `False`)
- **CONSUMER_GROUP_NAME**: The name of the consumer group to use when consuming from Kafka. (Default: `postgres-sink`, Required: `True`)
- **BATCH_SIZE**: The number of records that the sink holds before flushing data to PostgreSQL. (Default: `1000`, Required: `False`)
- **BATCH_TIMEOUT**: The number of seconds that the sink holds before flushing data to PostgreSQL. (Default: `1`, Required: `False`)

## Requirements / Prerequisites

You will need to have a PostgreSQL instance available and ensure that the connection details (host, port, database, user, and password) are correctly configured.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you, and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social media to show your appreciation.