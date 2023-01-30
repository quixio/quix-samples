# Python Postgres Database Sink

The sample contained in this folder gives an example on how to stream data from Quix to a Postgres Database, it handles both parameter and event data.

## Requirements / Prerequisites
 - A Postgres Database.

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


## Docs

Check out the [SDK docs](https://quix.io/docs/sdk/introduction.html) for detailed usage guidance.

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternatively, you can learn how to set up your local environment [here](https://quix.io/docs/sdk/python-setup.html).
