# Hugging Face Model

This python project generates a prediction with a Hugging Face: 
- It listens to the input topic for input data to predict on.
- It generates a prediction using the selected Hugging Face model.
- It outputs the class and score of the prediction to the selected output topic.

## Environment Variables

The different environment variables to populate are:

- **input**: Input topic with the original raw signal values
- **output**: Output topic where the alarm data will be populated
- **HuggingFaceModel**: Name of the Hugging Face model to be used. A list of available Hugging Face models can be found here: https://huggingface.co/models.
