# Snowflake

[This project](https://github.com/quixio/quix-library/tree/main/csharp/destinations/snowflake) allows the user to publish data from Quix to Snowflake, it handles both parameter and event data.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Setup & deploy` on the library item, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **Broker__TopicName**: Name of the input topic to read from.
- **Snowflake__Locator**: Locator of the account. Can be found under Admin/Accounts or in the URL.
- **Snowflake__Region**: Region of the account. Can be found under Admin/Accounts or in the URL.
  - e.g.: west-europe.azure. 
  - note: display name is used on Accounts page, but locator lets you copy the one needed. It should have the format of `https://{locator}.{region}.snowflakecomputer.com`
- **Snowflake__Database**: The name of the database to persist to      
- **Snowflake__User**: The username of the user the sink should use to interact with the database.
- **Snowflake__Password**: The password of the user configured above.

## Requirements / Prerequisites
 - A Snowflake account.

## Known limitations 
- Binary parameters are not supported in this version

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library) repo.

Please star us and mention us on social to show your appreciation.

