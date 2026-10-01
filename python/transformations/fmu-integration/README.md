# FMU Integration

This sample shows how to execute an FMU inside a Quix Streams application. It consumes messages from an input topic, runs the FMU for each message, and publishes enriched results to an output topic.


## How to use this sample

- Add a valid `.fmu` file to the app. It should be compiled for Linux if you plan to run it on Quix. The repo includes `simulink_example_inports.fmu` in this folder as an example.
- Edit the filename near the top of `main.py`:
```python
fmu_filename = "simulink_example_inports.fmu"
```

- When the app starts, it prints the FMU model variables with their `valueReference` and `causality` so you know which variables are inputs and outputs.
- Define the FMU_processing function according to your model inputs and outputs.

## Environment variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **output**: Name of the output topic to write to.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.