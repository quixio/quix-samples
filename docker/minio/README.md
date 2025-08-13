# MinIO

This sample demonstrates how to deploy and use MinIO in your pipeline.

## Using with a Quix Cloud Amazon S3 Connectors

This deployment will work seamlessly with the Quix Cloud Amazon S3 Source/Sink connectors.

Simply set your environment variables for either connector:

```shell
S3_BUCKET="<MINIO BUCKET NAME>"
AWS_ENDPOINT_URL="http://minio:80"
AWS_REGION_NAME="<ANY STR>"
AWS_ACCESS_KEY_ID: "<MINIO ROOT USERNAME>"
AWS_SECRET_ACCESS_KEY: "<MINIO ROOT PASSWORD>"

```

## How to Run

1. Log in or sign up at [Quix](https://portal.platform.quix.io/signup?xlink=github) and navigate to the Code Samples section.
2. Click **Deploy** to launch a pre-built container.
3. Fill in the required environment variables for your MinIO instance.
4. Enable state, otherwise changes will be lost on restart. Please note, the necessary storage type may not be supported on all Quix Platforms.

For more configuration options and details, refer to [MinIO's Docker Hub](https://hub.docker.com/r/minio/minio).


## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. The image is offered as-is, with no MinIO specific support from Quix.
