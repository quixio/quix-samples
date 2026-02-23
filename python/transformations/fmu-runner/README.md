# FMU Runner

[This template](https://github.com/quixio/quix-samples/tree/main/python/transformations/fmu-runner) demonstrates how to consume simulation requests from a Kafka topic, execute FMU (Functional Mock-up Unit) simulations using the [fmpy](https://github.com/CATIA-Systems/FMPy) library, and publish the results to an output topic:

- It listens to an input Kafka topic for simulation requests containing `.fmu` files.
- It executes the simulation using fmpy, applying any input data and parameter overrides.
- It outputs the simulation results (time series with all output variables) to another Kafka topic.

## How to run

Create a [Quix](https://login.quix.io/?utm_campaign=github) account or log-in and visit the Templates page to use this project.

Clicking `Deploy` on the Template, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Template, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code template uses the following environment variables:

- **input**: Name of the input topic to listen to for simulation requests. Default: `simulation`
- **output**: Name of the output topic to write simulation results to. Default: `simulation-results`
- **FMU_PATH**: Path to the FMU file to use for simulations. Default: `tests/fixtures/BouncingBall.fmu`

## Message format

### Input message

```json
{
  "message_key": "unique-request-id",
  "model_filename": "BouncingBall.fmu",
  "config": {
    "start_time": 0.0,
    "stop_time": 10.0,
    "parameters": {
      "e": 0.7
    }
  },
  "input_data": [
    {"time": 0.0, "input_var": 1.0},
    {"time": 1.0, "input_var": 2.0}
  ]
}
```

### Output message

```json
{
  "message_key": "unique-request-id",
  "status": "completed",
  "processing_time_ms": 150.5,
  "model_filename": "BouncingBall.fmu",
  "input_data": [
    {"time": 0.0, "h": 1.0, "v": 0.0, "position": 1.0},
    {"time": 0.1, "h": 0.95, "v": -0.98, "position": 0.95}
  ]
}
```

## Requirements/prerequisites

This service is a lightweight FMU runner that does **not** require MATLAB Runtime. It processes standard FMU 2.0 files using the fmpy library.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
