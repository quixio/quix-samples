# Postgres

[This project](https://github.com/quixio/quix-samples/tree/main/python/destinations/Postgres) gives an example of how to stream data from Quix to a Postgres Database, it handles both parameter and event data.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to read from.
- **PG_HOST**: The IP address or fully qualified domain name of your server.
- **PG_PORT**: The Port number to use for communication with the server.
- **PG_DATABASE**: The name of the database to persist to.
- **PG_USER**: The username of the sink should use to interact with the database.
- **PG_PASSWORD**: The password for the user configured above.
- **PG_SCHEMA**: The schema name of the tables.
- **MAX_QUEUE_SIZE**: Max queue size for the sink ingestion.

## Known limitations 
- Binary parameters are not supported in this version

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

