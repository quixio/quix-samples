# Threshold alert

[This project](https://github.com/quixio/quix-library/tree/main/python/transformations/Threshold-Alert) publishes messages when a certain numeric threshold is crossed. 
- Activates only once per threshold cross. 
- Works on either side of the threshold. 
- The signal value doesn't need to be equal to the threshold value for the alarm to go off.
- Keeps activating when the threshold is crossed (doesn't stop after it goes off the first time).
- You can configure the time between checks to control the number of messages published.

![graph](Threshold_Alert.png?raw=true)

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Setup & deploy` on the library item, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **input**: This is the input topic for raw data.
- **output**: This is the output topic for alerts.
- **parameterName**: This is the stream's parameter to track.
- **thresholdValue**: This is the threshold's numerical value.
- **bufferMilliSeconds**: How long to wait before waiting for threshold checking (milliseconds).

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library) repo.

Please star us and mention us on social to show your appreciation.

