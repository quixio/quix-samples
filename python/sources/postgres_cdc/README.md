# PostgreSQL CDC

[This connector](https://github.com/quixio/quix-samples/tree/main/python/sources/postgres_cdc) demonstrates how to capture changes to a PostgreSQL database table (using CDC) and publish the change events to a Kafka topic.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment variables

The connector uses the following environment variables:

- **output**: Name of the output topic to write into.
- **PG_SCHEMA**: The name of the schema for CDC.
- **PG_TABLE**: The name of the table for CDC.

The connection comes from the shared **`postgres-connection`** Variable Group, so this
source, the PostgreSQL Sink and the bundled PostgreSQL server all agree. These were
renamed from `PG_HOST` / `PG_PORT` / `PG_USER` / `PG_PASSWORD` / `PG_DATABASE`, which
still work for existing deployments:

- **POSTGRES_HOST**: Host address of the PostgreSQL instance (Default: `postgresql`)
- **POSTGRES_PORT**: Port of the PostgreSQL instance (Default: `80`)
- **POSTGRES_DB**: The name of the database for CDC (Default: `quix`)
- **POSTGRES_USER**: The username the source uses to interact with the database (Default: `admin`)
- **POSTGRES_PASSWORD**: The password for the user configured above

## Requirements / Prerequisites

- A Postgres Database.
- Set `wal_level = logical` in `postgresql.conf`.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
