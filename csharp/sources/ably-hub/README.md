# C# Ably Source
The sample contained in this folder gives an example on how to connect to sources in the [Ably Hub](https://ably.com/hub) and write values to a Quix stream.

## Requirements / Prerequisites
 - An active [Ably](https://ably.com/) subscription (The free account is ok too)

## Environment variables

The code sample uses the following environment variables:

- **output**: Name of the output topic to write into.
- **AblyToken**: The Ably API token to use.
- **AblyChannel**: The Ably Channel to listen to.
- **StreamId**: A name for the data stream.

## Choosing an Ably source

 - Go to the [Ably Hub](https://ably.com/hub) and pick a data source like 'Live Trains', 'Live Bitcoin' prices or 'Live Weather'.
 - Choose the "Shell script" option
 - Copy the API Key's value from the line beginning with "api_key" (note that this API key is usually only going to last 4 hours for the free Ably account)
 - Paste this into the AblyToken box in Quix

Repeat this for the "channel"

When you run the code it subscribes to the Ably data source you configured and streams the data into Quix.

## Docs
Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.
