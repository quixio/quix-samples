# Fraud detection II - clean

This is the clean stage for the fraud detection example. The cleaning consists mainly on the dummyfication of the categorical columns.

## Requirements/prerequisites

This is part of the fraud detection project:

- Fraud detection I - ingest: project that writes transaction data into topic.
- Fraud detection II - clean (this one): project that reads raw transaction data and cleans it (dummyfication).
- Fraud detection III - predict: project that writes the cleaned transaction data and uses it to predict fraud using a loaded machine learning model. 

## Environment variables

The code sample uses the following environment variables:

- **input**: This is the input topic for raw fraud data.
- **output**: This is the output topic for cleaned fraud data.

## Docs

Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternativelly, you can learn how to set upyour local environment [here](/python/local-development).

