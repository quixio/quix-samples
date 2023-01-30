# AWS S3 Sink

Publish data to S3.

## Requirements / Prerequisites

You'll need to have a S3 resource available on AWS and access credentials with permission to upload files to S3 buckets.

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **batch_time_interval**: Time interval in seconds to save data to S3 (set -1 to disable batching based on tme)
- **batch_msg_count**: Message count in the batch (0 saves data as they arrive, -1 disables batching based on message count).
- **parameter**: Name of the parameter to save to S3.
- **aws_access_key_id**: AWS S3 access key id.
- **aws_access_key**: AWS S3 access key
- **s3_bucket**: AWS S3 bucket.
- **s3_folder**: Name of the S3 folder to save to.
- **s3_folder_per_stream**: Flag to save different streams to different S3 folders.
- **prefix**: File name prefix.
- **suffix**: File suffix (e.g. file type extension).

## Docs

Check out the [SDK Docs](https://quix.io/docs/sdk/introduction.html) for detailed usage guidance

## How to Run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this application without a local environment setup.

Alternatively, you can check [here](https://quix.io/docs/sdk/python-setup.html) how to setup your local environment.