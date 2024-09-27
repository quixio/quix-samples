# Websocket Destination

This code sample demonstrates how to consume data from a Kafka topic using QuixStreams and send it to connected WebSocket clients.

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log in and visit the Code Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment Variables

The code sample uses the following environment variables:

- **input**: This is the input topic (Default: `input`, Required: `True`)
- **USERNAME**: Username for WebSocket authentication (Required: `True`)
- **PASSWORD**: Password for WebSocket authentication (Required: `True`)

## Configuration

If deploying to Quix Cloud you will need to create secrets for the username and password.
See the [docs](https://quix.io/docs/deploy/secrets-management.html) for more information on how to do this.

## Requirements / Prerequisites

You will need to have a Quix account and a Kafka topic to consume data from. 

## How it works

The application sets up a WebSocket server that listens for incoming connections. Clients can connect to the WebSocket server and authenticate using basic authentication. Once authenticated, clients can receive messages from the Kafka topic.

The server checks if the key of the incoming message matches any of the connected clients' paths or if any client is connected with a wildcard `*`. If a match is found, the message is sent to the respective clients.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.