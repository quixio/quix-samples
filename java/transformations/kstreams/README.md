# Kafka Streams Template

> **⚠️ Warning:** This template for now will work with Confluent broker only.

This code sample demonstrates how to consume data from an input Kafka topic, apply a simple transformation to that data, and publish the result to an output Kafka topic. It leverages the Kafka Streams library for stream processing within a Java application and prints relevant content to the console for monitoring and debugging.

This template is a foundation to build real-time data processing applications in Java using Kafka Streams.

## How to Run

1. **Set up a Kafka Environment**:
   - Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account, log in, and set up your Kafka broker details if using Quix as your Kafka provider.
   - Alternatively, ensure you have access to any Kafka environment for this application to connect.

2. **Clone or Fork the Project**:
   - Fork this template from the Quix [GitHub repository](https://github.com/quixio/quix-samples) or clone the project to customize it.

3. **Build and Run the Application**:
   - Build the project using Maven:
     ```bash
     mvn clean package
     ```
   - Run the application with the necessary environment variables (see below), or deploy it in your preferred environment (e.g., Docker, Kubernetes).

## Environment Variables

The code sample uses the following environment variables:

- **`input`**: The name of the input Kafka topic from which data is consumed.
- **`output`**: The name of the output Kafka topic to which transformed data is published.

To set these environment variables in a Unix-like terminal:
```bash
export input=<your_input_topic>
export output=<your_output_topic>
java -jar target/kafka-streams-app.jar

Or in Windows:

```bash
set input=<your_input_topic>
set output=<your_output_topic>
java -jar target/kafka-streams-app.jar
```

## Customizing the Transformation

This template provides a basic setup where data is consumed from an input topic, processed, and sent to an output topic. Modify the Kafka Streams code in the MessageCountPerSecond class (or your designated transformation class) to apply specific transformations to your data as needed.

For example:
	•	Apply aggregations or filtering.
	•	Enrich data by joining with another stream or table.
	•	Transform messages by mapping fields or values.

## Running with Docker

The provided Dockerfile allows you to build and run this Kafka Streams application inside a Docker container.

### Building the Docker Image

	1.	Open a terminal in the project’s root directory, where the Dockerfile is located.
	2.	Build the Docker image:

```bash
docker build -t kafka-streams-app .
```


### Running the Docker Container

To run the application in a Docker container, you’ll need to pass in the required environment variables (input and output):

```
docker run -e input=<your_input_topic> -e output=<your_output_topic> -p 8080:8080 kafka-streams-app
```
	•	Environment Variables: Use the -e flag to set the input and output environment variables.
	•	Port Mapping: If metrics or other HTTP endpoints are exposed, use the -p flag to map the container’s port (8080 in this example) to the host.

### Example

Here’s an example command to run the container with the topics input-topic and output-topic:

```bash
docker run -e input=input-topic -e output=output-topic -p 8080:8080 kafka-streams-app
```

The application will start inside the container, consuming data from the specified input topic, processing it, and publishing to the output topic.

## Contribute

Submit forked projects to the Quix GitHub repository. If your project is accepted, it will be attributed to you, and you’ll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our GitHub repository.

Please star the repo and share it on social media to support our community.

This should now provide a comprehensive guide for users to understand and run the Kafka Streams template, including instructions for Docker. Let me know if you’d like any additional details!