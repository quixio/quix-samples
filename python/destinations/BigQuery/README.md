# Python BigQuery Database Sink

The sample contained in this folder gives an example on how to stream data from Quix to a BigQuery Database, it handles both parameter and event data.

## Requirements / Prerequisites
 - A BigQuery Database.

## Environment variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to read from.
- **PROJECT_ID**: The BigQuery GCP Project ID.
- **DATASET_ID**: The target Biguqery dataset ID.
- **DATASET_LOCATION**: Location of BigQuery dataset.
- **SERVICE_KEY_PATH**: The path to the service key of the BigQuery GCP project.

## Known limitations 
- BigQuery fails to immediately recognise new Schema changes such as adding a new field when streaming insert data.
- BigQuery doesn't allow deleting data when streaming insert data.


## Docs

Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance.

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternatively, you can learn how to set up your local environment [here](https://quix.ai/docs/sdk/python-setup.html).

