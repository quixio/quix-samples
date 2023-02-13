# Fraud detection I - ingest

This is the ingestion stage for the Fraud Detection example. This sample will send public transaction data to a Topic at the rate of 5 rows per second.

## Requirements/prerequisites

This is part of the fraud detection project:

- Fraud detection I - ingest (this one): project that writes transaction data into topic.
- Fraud detection II - clean: project that reads raw transaction data and cleans it (dummyfication). 
- Fraud detection III - predict: project that writes the cleaned transaction data and uses it to predict fraud using a loaded machine learning model. 

## Environment variables

The code sample uses the following environment variables:

- **output**: This is the output topic for raw transaction data.

## Docs

Check out the [SDK docs](https://docs.quix.io/sdk-intro.html) for detailed usage guidance.

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternatively, you can learn how to set up your local environment [here](https://docs.quix.io/sdk/python-setup.html).

