# Percentage alert

This Python project generates an alert when certain percentage increase or decrease is achieved. 
- The percentage value is inserted in percentage points: 20 = 20%.
- It automatically updates last relative minima and maxima data values to works smartly on drifting signals and changing environments.

![graph](PercentageAlert.png?raw=true)

## Environment variables

The code sample uses the following environment variables:

- **input**: This is the input topic for numeric data.
- **output**: This is the output topic for alerts.
- **ParameterName**: The parameter name to track
- **PercentagePointsAlert**: Percentage points of increase/decrease for the alert to activate e.g. 10 is 10%, 20 is 20%, etc.

## Docs

Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance.

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternativelly, you can learn how to set up your local environment [here](https://quix.ai/docs/sdk/python-setup.html).


