# C# SQL Database Sink

The sample contained in this folder gives an example on how to stream data from Quix to a SQL Database, it handles both parameter and event data.

## Requirements / Prerequisites
 - A SQL Database.

## Environment variables

The code sample uses the following environment variables:

- **Broker__TopicName**: Name of the input topic to read from.
- **SqlServer__Server**: The IP address or fully qualified domain name of your server.
- **SqlServer__Port**: The Port number to use for communication with the server.
- **SqlServer__Database**: The name of the database to persist to.
- **SqlServer__User**: The username of the sink should use to interact with the database.
- **SqlServer__Password**: The password for the user configured above.

## Known limitations 
- Binary parameters are not supported in this version

## Docs
Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.
