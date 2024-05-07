# Flask Web Gateway

[This code sample](https://github.com/quixio/quix-samples/tree/develop/python/sources/web_api_gateway) demonstrates how to run a Flask web gateway and use it to publish to a Kafka topic via HTTP POST requests.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

Once you have deployed the Sample within your project there are three things to bear in mind:

1. Your data JSON must contain a "sessionId" key 
2. Keys and values must be Strings or Bytes.
3. The Flask gateway endpoint must end with `/data/`. E.g `https://gateway-example-develo.deployments.quix.io/data/`

## Environment variables

The code sample uses the following environment variables:

- **output**: This is the output topic for hello world data.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
