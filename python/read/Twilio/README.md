# Twilio sink

This python service will send data from Quix as text message using Twilio platform.

## Requirements / Prerequisites (optional)

This python service requires a [Twilio](https://www.twilio.com/es-mx/) account SID and Messaging Service SID.

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **numbers**: List of phone numbers to send messages to. Split ',' for multiple phone numbers.
- **account_sid**: Twilio account SID.
- **auth_token**: Twilio auth token.
- **messaging_service_sid**: Twilio message service SID.
- **message_limit**: Set the limit for how many messages are sent per minute.

## Docs

Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this application without a local environment setup.

Alternatively, you can check [here](/python/local-development) how to setup your local environment.