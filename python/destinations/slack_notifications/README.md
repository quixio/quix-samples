# Slack Notifications

[This code sample](https://github.com/quixio/quix-samples/tree/develop/python/destinations/slack_notifications) demonstrates how to consume data from a Kafka topic and trigger a Slack webhook based on specific matching critera that you apply to the incoming data.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **webhook_url**: The webhook url to send notifications to

## Requirements / Prerequisites

You'll need to have access to Slack and be able to set up a webhook here: https://api.slack.com/apps

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
