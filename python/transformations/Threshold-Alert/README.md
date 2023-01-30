# Threshold alert

This Python project publishes messages when a certain numeric threshold is crossed. 
- It activates only once per threshold cross. 
- It works on either side of the threshold. 
- The signal value doesn't need to be equal to the threshold value for the alarm to go off.
- It keeps activating when the threshold is crossed (doesn't stop after it goes off the first time).
- You can configure the time between checks to control the number of messages published.

![graph](Threshold_Alert.png?raw=true)

## Environment variables

The code sample uses the following environment variables:

- **input**: This is the input topic for raw data.
- **output**: This is the output topic for alerts.
- **parameterName**: This is the stream's parameter to track.
- **thresholdValue**: This is the threshold's numerical value.
- **bufferMilliSeconds**: How long to wait before waiting for threshold checking (milliseconds).

## Docs

Check out the [SDK docs](https://quix.io/docs/sdk/introduction.html) for detailed usage guidance.

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternatively, you can learn how to set up your local environment [here](https://quix.io/docs/sdk/python-setup.html).