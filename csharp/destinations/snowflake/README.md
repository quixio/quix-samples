# C# Snowflake Sink

The sample contained in this folder gives an example on how to stream data from Quix to Snowflake, it handles both parameter and event data.

## Requirements / Prerequisites
 - An AWS account with Snowflake installed.

## Environment variables

The code sample uses the following environment variables:

- **Snowflake__AccessKeyId**: Obtained from your AWS account.
- **Snowflake__SecretAccessKey**: Obtained from your AWS account.
- **Snowflake__Region**: The region of your Snowflake database. Example: us-east-1
- **Snowflake__DatabaseName**: The Snowflake database to push data to

## Known limitations 
- Snowflake only support limited number of columns. This might be an issue with extensive amount of parameters or events
- Binary parameters are not supported in this version
- Stream metadata is not persisted in this version

## Docs
Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.
