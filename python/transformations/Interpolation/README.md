# Interpolation

[This project](https://github.com/quixio/quix-samples/tree/main/python/transformations/Interpolation) performs linear interpolations over a selected parameter list. 
- It calculates the time delta between the last data parameters received. 
- It calculates the average of the last two parameters received.

![graph](Interpolation.png?raw=true)

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **input**: This is the input topic for raw data.
- **output**: This is the output topic for the windowed data.
- **Parameters**: The stream's parameter to perform the window function upon. Add them as: "ParameterA,ParameterB,ParameterC,etc.".

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

