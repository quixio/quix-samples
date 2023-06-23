# Fraud detection - Ingest

[This project](https://github.com/quixio/quix-samples/tree/main/python/sources/Fraud-Ingest) is the ingestion stage for the Fraud Detection example. This sample will publish transaction data to a topic at the rate of 5 rows per second.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **output**: This is the output topic for raw transaction data.

## Requirements/prerequisites

This is part of the fraud detection project:

- Fraud detection I - Ingest (this one): project that writes transaction data into topic.
- Fraud detection II - Cleaning: project that reads raw transaction data and cleans it (dummyfication). 
- Fraud detection III - Prediction: project that writes the cleaned transaction data and uses it to predict fraud using a loaded machine learning model. 


## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

