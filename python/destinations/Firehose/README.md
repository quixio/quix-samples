# Firehose

[This project](https://github.com/quixio/quix-samples/tree/main/python/destinations/Firehose) publishes data to an AWS Kinesis Firehose.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

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

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

