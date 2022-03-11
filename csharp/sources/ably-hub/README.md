# C# Ably Source
This sample is a connector to Ably. It lets you subscribe to any channel as a source for your Quix application.

You can also use it to stream data from [Ably's Hub](https://ably.com/hub) to quickly access open data.

## Requirements / Prerequisites
 - An active [Ably](https://ably.com/) subscription (The free account is ok too)

## Environment variables

The code sample uses the following environment variables:

- **output**: Name of the output topic to write into.
- **AblyToken**: The Ably API token to use.
- **AblyChannel**: The Ably Channel to subscribe to.
- **StreamId**: A name for the data stream.

## Choosing an Ably source

 - Go to the [Ably Hub](https://ably.com/hub) or your Ably account.
 - Pick a data source like 'Live Trains', 'Live Bitcoin' or one of your own channels.
 - Choose the "Shell script" option in the Hub, or "Your App"/"API Keys" from the dashboard.
 - Copy the API Key (note that this API key is usually only going to last 4 hours for the free Ably account)
 - Paste this into the AblyToken box in Quix

Repeat this for the "channel"

When you run the code it subscribes to the Ably data source you configured and streams the data into Quix.

## Docs
Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.
