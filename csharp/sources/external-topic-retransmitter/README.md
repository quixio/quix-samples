# External Topic Retransmitter

Simple c# service which reads from an external topic and writes the content into a topic in current workspace.

## Environment variables

This code sample uses the following environment variables:

- **Source__Workspace__SdkToken**: The SDK token to use when reading from the source topic. 
- **Source__Workspace__Topic**: The name or id of the source topic.
- **Output__Topic**: The name or id of the target topic
- **Source__UseConsumerGroup**: (Optional) Whether a consumer group should be used.
- **Source__ConsumerGroup**: (Optional) The consumer group. If not provided, defaults to environment variable `Quix__Deployment__Id`. 
- **Source__Offset**: Where source should be join. `Earliest` will join from the very beginning, while `Latest` will only read new messages.

## Docs

Check out the [SDK docs](https://quix.io/docs/sdk/introduction.html) for detailed usage guidance.

## How to run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.