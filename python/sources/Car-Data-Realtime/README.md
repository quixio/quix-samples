# Real-time car CSV data

Write data from a CSV into a stream in realtime at a given rate. This is a Python code sample for writing vehicle telemetry data (time series parameters) into the Quix platform. The example file ([cardata.csv](source/cardata.csv)) is data collected from a virtual F1&reg; car in **Codemasters 2019 racing game**. This data was acquired using our **Codemaster F1&reg; 2019 bridge**. 

## Environment variables

The code sample uses the following environment variables:

- **output**: This is the output topic for car data.
- **seconds_to_wait**: Seconds to wait between each data row writing.

## Docs
Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance.

## How to run
Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account to edit or deploy this application without a local environment setup.

Alternatively, you can learn how to set up your local environment [here](https://quix.ai/docs/sdk/python-setup.html).