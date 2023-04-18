# Ably

[This project](https://github.com/quixio/quix-samples/tree/main/csharp/sources/ably-hub) is a connector to Ably. It helps you subscribe to any channel as a source for your Quix application.

You can also use it to stream data from [Ably's Hub](https://ably.com/hub) to quickly access open data.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Setup & deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **output**: Name of the output topic to write into.
- **AblyToken**: The Ably API token to use.
- **AblyChannel**: The Ably Channel to subscribe to.
- **StreamId**: A name for the data stream.

## Requirements / Prerequisites
 - An active [Ably](https://ably.com/) subscription (The free account is ok too)

## Choosing an Ably source

 - Go to the [Ably Hub](https://ably.com/hub) or your Ably account.
 - Pick a data source like 'Live Trains', 'Live Bitcoin' or one of your own channels.
 - Choose the "Shell script" option in the Hub, or "Your App"/"API Keys" from the dashboard.
 - Copy the API Key (note that this API key is usually only going to last 4 hours for the free Ably account)
 - Paste this into the AblyToken box in Quix

Repeat this for the "channel"

When you run the code it subscribes to the Ably data source you configured and streams the data into Quix.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

