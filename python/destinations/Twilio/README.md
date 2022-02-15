# Twilio sink

This Python service will send data from Quix as text message using Twilio platform.

## Requirements/prerequisites

This Python service requires a [Twilio](https://www.twilio.com) account SID and Messaging Service SID.

## Environment variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **numbers**: List of phone numbers to send messages to. Split ',' for multiple phone numbers.
- **account_sid**: Twilio account SID.
- **auth_token**: Twilio auth token.
- **messaging_service_sid**: Twilio message service SID.
- **message_limit**: Set the limit for how many messages are sent per minute.

## Docs

Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance.

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternativelly, you can learn how to set up your local environment [here](/python/local-development).