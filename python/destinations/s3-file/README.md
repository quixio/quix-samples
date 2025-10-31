# AWS S3 File Destination

[This connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/s3-file) demonstrates how to consume data from a Kafka topic and write it to an AWS S3 bucket.

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment Variables

The connector uses the following environment variables (which generally correspond to the 
[`S3FileSink`](https://quix.io/docs/quix-streams/connectors/sinks/amazon-s3-sink.html) parameter names):

### Required
- `input`: The input Kafka topic
- `S3_BUCKET`: The S3 bucket to use.
- `AWS_ENDPOINT_URL`: The URL to your S3 instance.
- `AWS_REGION_NAME`: The region of your S3 bucket.
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret.
- `AWS_ACCESS_KEY_ID`: Your AWS Access Key.

### Optional
Unless explicitly defined, these are optional, or generally set to the [`S3FileSink`](https://quix.io/docs/quix-streams/connectors/sinks/amazon-s3-sink.html) defaults.

- `S3_BUCKET_DIRECTORY`: An optional path within the S3 bucket to use.  
  **Default**: "" (root)
- `FILE_FORMAT`: The file format to publish data as; options: \[parquet, json\].  
  **Default**: "parquet"


## Requirements / Prerequisites

You will need the appropriate AWS features and access to use this connector.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
