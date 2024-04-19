# Segment

[This code sample](https://github.com/quixio/quix-samples/tree/develop/python/sources/segment_webhook) demonstrates how to connect to Segment, read event data and publish that data to a Kafka topic.

It's secure, using a secret shared with both Quix and Segment.

And we've used Waitress “… a production-quality pure-Python WSGI server with very acceptable performance. It has no dependencies except ones that live in the Python standard library. It runs on CPython on Unix and Windows.”

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

This code sample uses the following environment variables:

- **output**: The output topic to stream Segment data into
- **shared_secret**: The secret you configured in Segment

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
