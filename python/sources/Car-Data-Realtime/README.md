# Real-time vehicle telemetry

[This project](https://github.com/quixio/quix-library/tree/main/python/sources/Car-Data-Realtime) publishes data from a CSV file  in realtime at a given rate. 

This is a Python code sample for publishing vehicle telemetry data (time series parameters) into the Quix platform. The example file `cardata.csv` is data collected from a virtual F1&reg; car in **Codemasters 2019 F1&reg; racing game**. This data was acquired using our [**Codemaster F1&reg; 2019 project**](https://github.com/quixio/quix-library/tree/main/csharp/advanced/Bridge.Codemasters). 

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Setup & deploy` on the library item, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **output**: This is the output topic for car data.
- **seconds_to_wait**: Seconds to wait between each data row writing.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library) repo.

Please star us and mention us on social to show your appreciation.

