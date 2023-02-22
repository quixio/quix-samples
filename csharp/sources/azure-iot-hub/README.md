# Azure IoT Hub

[This project](https://github.com/quixio/quix-library/tree/main/csharp/sources/azure-iot-hub){target="_blank"} gives an example of how to subscribe to data in an Azure IoT Hub and publish it to  Kafka using the Quix SDK.

![graph](iot-bridge.png?raw=true)

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Setup & deploy` on the library item, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **output**: This is the output topic where data will be written to.
- **connectionString**: This is the Event Hub connection string.
- **eventHubName**: This is the Event Hub name.

### Connection to Quix

In this code snippet, the service connects to the Kafka topic in Quix. Use the Library page in the Quix portal to generate this code for a particular topic in your workspace.
```csharp
 // Create a client factory. The Factory helps you create a QuixStreamingClient (see below) more easily
var client = new Quix.Sdk.Streaming.QuixStreamingClient();

// Create a QuixStreamingClient (using the factory) in order to create new streams for the above configured topic
using var outputTopic = client.OpenOutputTopic("{placeholder:outputTopic}");
```

### Transformation to Quix SDK format

In code example we simply get the whole JSON message and send it as an event with the Quix SDK.

```csharp
var data = Encoding.UTF8.GetString(partitionEvent.Data.Body.ToArray());

stream.Events
	.AddTimestamp(partitionEvent.Data.EnqueuedTime.ToUniversalTime().DateTime)
	.AddValue("message", data)
	.Write();
```

but in a real application, we suggest developing a model to parse this data and publish it using the Quix SDK. 

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library){target="_blank"} repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library){target="_blank"} repo.

Please star us and mention us on social to show your appreciation.

