# C# Ably Sink

The sample contained in this folder gives an example on how to stream data from Quix to Ably, it handles both parameter and event data.

Quix Parameter Data is streamed to an Ably with a message name prefixed with whatever you choose and postfixed with '-parameter-data'
Quix Event Data is prefixed with whatever you choose and postfixed with '-event-data'

## Requirements / Prerequisites
 - An active [Ably](https://ably.com/) subscription (The free account is ok too)

## Environment variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to read from.
- **AblyToken**: The Ably API token to use.
- **AblyChannel**: The Ably Channel to send to.
- **AblyMessageNamePrefix**: The prefix for the Ably Message Name.

## Docs
Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.
