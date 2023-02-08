# Python Postgres Database CDC Source

The sample contained in this folder gives an example on how to stream data from Postgres Database CDC to Quix, it handles both parameter and event data.

## Requirements / Prerequisites
 - A Postgres Database.
 - Set `wal_level = logical` in `postgresql.conf`.

## Environment variables

The code sample uses the following environment variables:

- **output**: Name of the output topic to write into.
- **PG_HOST**: The IP address or fully qualified domain name of your server.
- **PG_PORT**: The Port number to use for communication with the server.
- **PG_DATABASE**: The name of the database for CDC.
- **PG_USER**: The username of the sink should use to interact with the database.
- **PG_PASSWORD**: The password for the user configured above.
- **PG_SCHEMA**: The name of the schema for CDC.
- **PG_TABLE**: The name of the table for CDC.

## Known limitations


## Docs

Check out the [SDK docs](https://docs.quix.io/sdk-intro.html) for detailed usage guidance.

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternatively, you can learn how to set up your local environment [here](https://docs.quix.io/sdk/python-setup.html).