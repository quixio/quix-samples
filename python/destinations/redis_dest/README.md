

# Redis Destination

Write data to Redis from Quix. This code sample is a Quix destination that writes data to Redis.
It can be used to write data from any Quix source to Redis.

This sample will write JSON data to Redis.
We assume that the incoming data will have a `key` field, this will be combined with the `redis_key_prefix` environment variable to create the Redis key where data will be stored.

Note that you need [Redis Stack](https://redis.io/docs/about/about-stack/) to use this code sample.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log in and visit the Code Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment Variables

The code sample uses the following environment variables:

- **input**: This is the input topic (Default: `input`, Required: `True`)
- **redis_host**: Host address for the Redis instance (Required: `True`)
- **redis_host**: Host address for the Redis instance (Required: `True`)
- **redis_port**: Port for the Redis instance (Default: `6379`, Required: `True`)
- **redis_password**: Password for the Redis instance (Default: `None`, Required: `False`)
- **redis_username**: Username for the Redis instance (Default: `None`, Required: `False`)
- **redis_key_prefix**: The prefix for the key to store data under.

## Requirements / Prerequisites

You will need to have a Redis Stack database. Either you can use the [Redis Cloud](https://redis.com/cloud/overview/) or
you can install Redis locally. You can find the instructions to [install Redis locally](https://redis.io/docs/install/install-stack/).

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.

