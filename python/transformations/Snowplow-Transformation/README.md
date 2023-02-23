# Snowplow transformation

[This project](https://github.com/quixio/quix-library/tree/main/python/transformations/Snowplow-Transformation){target="_blank"} transforms your raw Snowplow data into Quix format.

This transformation uses the Snowplow analytics SDK and Pandas to convert the incoming data to Quix format.

Configure and deploy the [Kinesis](https://github.com/quixio/quix-library/tree/main/python/sources/AmazonKinesis){target="_blank"} connector, then deploy this to convert the data.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Setup & deploy` on the library item, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **input**: This is the input topic for raw data.
- **output**: This is the output topic for converted stream.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library){target="_blank"} repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library){target="_blank"} repo.

Please star us and mention us on social to show your appreciation.

