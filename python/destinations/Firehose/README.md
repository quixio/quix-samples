# Amazon DynamoDB Sink

Publishes data to Amazon Kinesis Data Firehose.

## Requirements / Prerequisites

AWS access key id and secret for a user having permission to perform `firehose:PutRecordBatch` on supplied `stream_name`

### Example policy for Firehose stream

```json
{
  "Effect": "Allow",
  "Action": [
    "firehose:PutRecordBatch"
  ],
  "Resource": [
    "arn:aws:firehose:region:account-id:deliverystream/stream_name"
  ]
}
```

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to. `Required`
- **stream_name**: Name of the Amazon Kinesis Data Firehose stream. `Required`
- **aws_access_key_id**: AWS access key id. `Required`
- **aws_secret_access_key**: AWS secret access key `Required`
- **batch_msg_count**: Number of messages to push as a part of single batch write. Maximum supported: 500

## Docs

Check out the [SDK Docs](https://docs.quix.io/sdk-intro.html) for detailed usage guidance

## How to Run

Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this
application without a local environment setup.

Alternatively, you can check [here](https://docs.quix.io/sdk/python-setup.html) how to setup your local environment.