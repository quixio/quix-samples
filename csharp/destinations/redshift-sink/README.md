# Redshift

[This project](https://github.com/quixio/quix-library/tree/main/csharp/destinations/redshift-sink) gives an example of how to stream data from Quix to AWS Redshift, it handles both parameter and event data.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Setup & deploy` on the library item, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **Redshift__AccessKeyId**: Obtained from your AWS account.
- **Redshift__SecretAccessKey**: Obtained from your AWS account.
- **Redshift__Region**: The region of your Redshift database. Example: us-east-1
- **Redshift__DatabaseName**: The Redshift database to push data to

## Known limitations 
- Redshift only supports a limited number of columns. This might be an issue with large numbers of parameters or events
- Binary parameters are not supported in this version
- Stream metadata is not persisted in this version

## Requirements / Prerequisites
 - An AWS account with Redshift installed.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library) repo.

Please star us and mention us on social to show your appreciation.
