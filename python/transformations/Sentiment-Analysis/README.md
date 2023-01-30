# Hugging Face model

This python project generates a prediction with a [Hugging Face](https://huggingface.co/) model: 
- It listens to the input topic for input data to predict on.
- It generates a prediction using the selected Hugging Face model.
- It outputs the class and score of the prediction to the selected output topic.

## Requirements/prerequisites
When deploying this Python project, ensure you allow enough computational resources to host and execute the Hugging Face pipeline objects.

## Environment variables

The code sample uses the following environment variables:

- **input**: This is the raw data input topic.
- **output**: This is the output for the hugging face model score.
- **HuggingFaceModel**: Name of the Hugging Face model to be used. A list of available Hugging Face models can be found [here](https://huggingface.co/models).
- **TextColumnName**: "For the table structured input, name of the column where input text to perform predictions on."

## Docs

Check out the [SDK docs](https://quix.io/docs/sdk/introduction.html) for detailed usage guidance.

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternatively, you can learn how to set up your local environment [here](https://quix.io/docs/sdk/python-setup.html).

