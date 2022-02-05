# Percentage Alert

This python project generates an alert when certain percentage increase or decrease is achieved. 
- The percentage value is inserted in percentage points: 20 = 20%.
- It automatically updates last relative minima and maxima data values to works smartly on drifting signals and changing environments.

![Percentage_Alert](PercentageAlert.png?raw=true)

## Environment Variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **output**: Name of the output topic to write into.
- **ParameterName**: Parameter in the input topic of the specific signal that we want to apply the alert to
- **PercentagePointsAlert**: Percentage points that the signal has to vay for the alert to activate. 10 = 10%, 20=20%, etc.

## Docs

Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this application without a local environment setup.

Alternatively, you can check [here](/python/local-development) how to setup your local environment.


