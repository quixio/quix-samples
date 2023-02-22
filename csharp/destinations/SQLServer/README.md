# SQL Database

[This project](https://github.com/quixio/quix-library/tree/main/csharp/destinations/SQLServer){target="_blank"} gives an example of how to publish data from Quix to a SQL Database, it handles both parameter and event data.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Setup & deploy` on the library item, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

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

Check out the [SDK docs](https://docs.quix.io/sdk-intro.html) for detailed usage guidance

## How to run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library){target="_blank"} repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library){target="_blank"} repo.

Please star us and mention us on social to show your appreciation.

