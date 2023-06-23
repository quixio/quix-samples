# Ably sink connector

[This project](https://github.com/quixio/quix-samples/tree/main/csharp/destinations/ably-sink) is an example of how to stream data from Quix to Ably. It handles both time-series and event data.

Time-series Data is streamed to Ably with a message name prefixed with whatever you choose and postfixed with '-parameter-data'
Quix Event Data is prefixed with whatever you choose and postfixed with '-event-data'

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to read from.
- **AblyToken**: The Ably API token to use.
- **AblyChannel**: The Ably Channel to send to.
- **AblyMessageNamePrefix**: The prefix for the Ably Message Name.

## Prerequisites
 - An active [Ably](https://ably.com/) subscription (The free account is ok too)

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.