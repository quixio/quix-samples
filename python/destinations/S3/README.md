# S3

Publish data to an S3 bucket with [this project](https://github.com/quixio/quix-samples/tree/main/python/destinations/S3).

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **batch_time_interval**: Time interval in seconds to save data to S3 (set -1 to disable batching based on tme)
- **batch_msg_count**: Message count in the batch (0 saves data as they arrive, -1 disables batching based on message count).
- **parameters**: Comma separated list of parameters to look for in the received data.
- **aws_access_key_id**: AWS S3 access key id.
- **aws_access_key**: AWS S3 access key
- **s3_bucket**: AWS S3 bucket.
- **s3_folder**: Name of the S3 folder to save to.
- **s3_folder_per_stream**: Flag to save different streams to different S3 folders.
- **prefix**: File name prefix.
- **suffix**: File suffix (e.g. file type extension).
- **timezone**: A valid timezone from the IANA Time Zone Database e.g. GMT or US/Eastern or Asia/Singapore used for orchestrating time-based batching and file naming.

## Requirements / Prerequisites

You'll need to have a S3 resource available on AWS and access credentials with permission to upload files to S3 buckets.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
