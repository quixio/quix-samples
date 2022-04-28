# C# SqlServer Sink

The sample contained in this folder gives an example on how to stream data from Quix to SqlServer, it handles both parameter and event data.

## Requirements / Prerequisites
 - A SqlServer account.

## Environment variables

The code sample uses the following environment variables:

- **Broker__TopicName**: Name of the input topic to read from.
- **SqlServer__Locator**: Locator of the account. Can be found under Admin/Accounts or in the URL.
- **SqlServer__Region**: Region of the account. Can be found under Admin/Accounts or in the URL.
  - e.g.: west-europe.azure. 
  - note: display name is used on Accounts page, but locator lets you copy the one needed. It should have the format of `https://{locator}.{region}.SqlServercomputer.com`
- **SqlServer__Database**: The name of the database to persist to      
- **SqlServer__User**: The username of the user the sink should use to interact with the database.
- **SqlServer__Password**: The password of the user configured above.

## Known limitations 
- Binary parameters are not supported in this version

## Docs
Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.
