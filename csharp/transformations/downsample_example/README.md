# Downsample example

[This project](https://github.com/quixio/quix-samples/tree/main/csharp/transformations/downsample_example) gives an example of how to create a simple model that downsamples 100Hz data to 10Hz using the built in buffer.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment Variables

The code sample uses the following environment variables:

- **input**: This is the input topic for data to be downsampled.
- **output**: This is the output topic for downsampled data.

## Content of the sample
- HelloWorldModel.sln: The solution file describing what projects to include
- HelloWorldModel/Program.cs: contains logic necessary to connect to kafka topic and read stream, downsample data and write it back to kafka in different topic.
- HelloWorldModel/HelloWorldModel.csproj: the project file which holds together the project and describes some build related details

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

