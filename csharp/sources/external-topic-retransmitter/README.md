# External topic retransmitter

[This project](https://github.com/quixio/quix-samples/tree/main/csharp/sources/external-topic-retransmitter) is a simple C# service which subscribes to an external topic and publishes the data to a topic in the current workspace.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Setup & deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

This code sample uses the following environment variables:

- **Source__Workspace__SdkToken**: The SDK token to use when reading from the source topic. 
- **Source__Workspace__Topic**: The name or id of the source topic.
- **Output__Topic**: The name or id of the target topic
- **Source__UseConsumerGroup**: (Optional) Whether a consumer group should be used.
- **Source__ConsumerGroup**: (Optional) The consumer group. If not provided, defaults to environment variable `Quix__Deployment__Id`. 
- **Source__Offset**: Where source should be join. `Earliest` will join from the very beginning, while `Latest` will only read new messages.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

