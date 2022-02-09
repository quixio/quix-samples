# C# Downsample example
The sample contained in this folder gives an example on how to create a simple model that downsample 100Hz parameter to 10Hz using built in buffer.

## Environment Variables

The code sample uses the following environment variables:

- **input**: This is the input topic for data to be downsampled.
- **output**: This is the output topic for downsampled data.

## Content of the sample
- HelloWorldModel.sln: The solution file describing what projects to include
- HelloWorldModel/Program.cs: contains logic necessary to connect to kafka topic and read stream, downsample data and write it back to kafka in different topic.
- HelloWorldModel/HelloWorldModel.csproj: the project file which holds together the project and describes some build related details

## Docs

Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this application without a local environment setup.
