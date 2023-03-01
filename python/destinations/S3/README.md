# S3

Publish data to an S3 bucket with [this project](https://github.com/quixio/quix-library/tree/main/python/destinations/S3).

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Setup & deploy` on the library item, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

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

## Requirements / Prerequisites

You'll need to have a S3 resource available on AWS and access credentials with permission to upload files to S3 buckets.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library) repo.

Please star us and mention us on social to show your appreciation.

