# Streaming demo - input processing

Transform the raw data from the phone and send it back to the next pipeline stage. 

This is part of our [car demo](https://quix.io/data-stream-processing-example/) example which your can try [here](https://quix.io/demos/cardemo/qr).

## Requirements/prerequisites

In order to make use of this solution you also need to deploy the following projects:
 - Streaming demo - UI
 - Streaming demo - input (this one)
 - Streaming demo - control

## Environment variables

The code sample uses the following environment variables:

- **input**: This is the input topic for data from the phone.
- **output**: This is the output topic for parameters affecting game and vehicle control.

## Docs
Check out the [SDK docs](https://quix.io/docs/sdk/introduction.html) for detailed usage guidance.

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternatively, you can learn how to set up your local environment [here](https://quix.io/docs/sdk/python-setup.html).