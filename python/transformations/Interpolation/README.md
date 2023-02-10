# Interpolating function

This Python project performs linear interpolations over a selected parameter list. 
- It calculates the time delta between the last data parameters received. 
- It calculates the average of the last two parameters received.

![graph](Interpolation.png?raw=true)

## Environment variables

The code sample uses the following environment variables:

- **input**: This is the input topic for raw data.
- **output**: This is the output topic for the windowed data.
- **Parameters**: The stream's parameter to perform the window function upon. Add them as: "ParameterA,ParameterB,ParameterC,etc.".


## Docs
Check out the [SDK Docs](https://docs.quix.io/sdk-intro.html) for detailed usage guidance

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternatively, you can learn how to set up your local environment [here](https://docs.quix.io/sdk/python-setup.html).

