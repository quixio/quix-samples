# Snowplow

Using [this project](https://github.com/quixio/quix-library/tree/main/python/sources/Snowplow) you can connect your Snowplow data to a Quix topic.

Note that this connector works with Snowplow instances on AWS Kinesis, so you will need connection details Kinesis.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Setup & deploy` on the library item, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **output**: This is the Quix Topic that will receive the stream.
- **aws_access_key_id**: AWS Access Key Id.
- **aws_secret_access_key**: AWS Secret Access Key.
- **aws_region_name**: AWS Region Name.
- **aws_stream_name**: The name of the AWS stream you want to use.   

## Requirements/prerequisites

You will need Snowplow deployed to AWS to use this project.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library) repo.

Please star us and mention us on social to show your appreciation.

