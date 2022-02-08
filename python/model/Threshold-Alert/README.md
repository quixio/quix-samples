# Threshold Alert

This python project generates an alert when certain numeric threshold is crossed. 
- It activates only once per threshold cross. 
- It works at both sides of the threshold. 
- The signal value doesn't need to be equal to the threshold value for the alarm to go off.
- It keeps activating when the threshold is crossed (doesn't stop after it goes off the first time).

<img src='threshold_alert.png' width='400px' alt='graph'>

## Environment Variables

The code sample uses the following environment variables:

- **input**: This is the input topic for raw data.
- **output**: This is the output topic for alerts.
- **ParameterName**: This is the stream's parameter to track.
- **ThresholdValue**: This is the threshold's numerical value.

## Docs

Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this application without a local environment setup.

Alternatively, you can check [here](/python/local-development) how to setup your local environment.