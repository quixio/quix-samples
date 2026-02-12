# FMU Runner

[This code sample](https://github.com/quixio/quix-samples/tree/main/python/transformations/fmu-runner) demonstrates how to consume simulation requests from a Kafka topic, execute FMU (Functional Mock-up Unit) simulations using the [fmpy](https://github.com/CATIA-Systems/FMPy) library, and publish the results to an output topic:

- It listens to an input Kafka topic for simulation requests containing `.fmu` files.
- It downloads the FMU model binary from S3/MinIO storage (with local caching).
- It executes the simulation using fmpy, applying any input data and parameter overrides.
- It outputs the simulation results (time series with all output variables) to another Kafka topic.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to for simulation requests. Default: `simulation`
- **output**: Name of the output topic to write simulation results to. Default: `simulation-results`
- **S3_ENDPOINT**: S3/MinIO endpoint URL for fetching FMU model binaries. Default: `http://minio:80`
- **S3_ACCESS_KEY**: S3 access key ID.
- **S3_SECRET_KEY**: S3 secret access key.
- **S3_BUCKET**: S3 bucket name where FMU models are stored. Default: `fmu-models`

## Message format

### Input message

```json
{
  "message_key": "unique-request-id",
  "model_filename": "BouncingBall.fmu",
  "model_s3_path": "models/abc123_BouncingBall.fmu",
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

You will need:
- An S3-compatible storage service (MinIO, AWS S3, etc.) to host FMU model files.
- FMU models must be uploaded to the configured S3 bucket before running simulations.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
