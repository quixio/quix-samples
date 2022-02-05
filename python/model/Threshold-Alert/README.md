# Threshold Alert

This python project generates an alert when certain numeric threshold is crossed. 
- It activates only once per threshold cross. 
- It works at both sides of the threshold. 
- The signal value doesn't need to be equal to the threshold value for the alarm to go off.
- It keeps activating when the threshold is crossed (doesn't stop after it goes off the first time).

![Threshold_Alert](Threshold_Alert.png?raw=true)

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **output**: Name of the output topic to write into.
- **ParameterName**: Parameter in the input topic of the specific signal that we want to apply the alert to.
- **ThresholdValue**: Numerical value of the threshold.

## Docs

Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this application without a local environment setup.

Alternatively, you can check [here](/python/local-development) how to setup your local environment.