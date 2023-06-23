# Twilio

Using [this project](https://github.com/quixio/quix-samples/tree/main/python/destinations/Twilio) you can publish data to Twilio from a Quix topic.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **numbers**: List of phone numbers to send messages to. Split ',' for multiple phone numbers.
- **account_sid**: Twilio account SID.
- **auth_token**: Twilio auth token.
- **messaging_service_sid**: Twilio message service SID.
- **message_limit**: Set the limit for how many messages are sent per minute.

## Requirements/prerequisites

This Python service requires a [Twilio](https://www.twilio.com) account SID and Messaging Service SID.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

