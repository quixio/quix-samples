# Hugging Face Model

This python project generates a prediction with a [Hugging Face](https://huggingface.co/) model: 
- It listens to the input topic for input data to predict on.
- It generates a prediction using the selected Hugging Face model.
- It outputs the class and score of the prediction to the selected output topic.

## Requirements / Prerequisites
When deploying this python project, ensure you allow enough computational resources to host and execute the Hugging Face pipeline objects.

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **output**: Name of the output topic to write into.
- **HuggingFaceModel**: Name of the Hugging Face model to be used. A list of available Hugging Face models can be found [here](https://huggingface.co/models).


## Docs
{This will contain any reference/link to additional documentation or resource available related with the code}

Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this application without a local environment setup.

Alternativelly, you can check [here](/python/local-development) how to setup your local environment.

