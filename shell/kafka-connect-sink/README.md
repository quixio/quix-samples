# Kafka Connect Sink

[This template](https://github.com/quixio/quix-samples/tree/main/shell/kafka-connect-sink) provides a generic framework for running any Kafka Connect sink connector in Quix, allowing you to stream data from Kafka topics to external systems like Snowflake, PostgreSQL, MongoDB, S3, etc.

## Getting started

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Templates` tab to use this template.

Then either:
- **Deploy** immediately to your workspace 
- **Customize** to modify the code or configuration before deployment

## How it works

1. **Deploy the template** with your chosen connector from [Confluent Hub](https://www.confluent.io/hub)
2. **Configure the connection** by editing `connector.properties` with your external system credentials
3. **Data flows automatically** from your Kafka input topic to the destination system

## Environment variables

The template uses the following environment variables:

- **input**: The name of the input topic to sink data from.
- **CONNECT_OFFSET_STORAGE_TOPIC**: Topic name to use for storing offsets for Kafka Connect.
- **CONNECT_CONFIG_STORAGE_TOPIC**: Topic name to use for storing connector and task configurations for Kafka Connect.
- **CONNECT_STATUS_STORAGE_TOPIC**: Topic name to use for storing statuses for Kafka Connect.
- **CONNECTOR_NAME**: **(Required)** The [Confluent Hub](https://www.confluent.io/hub) Kafka connector to use. Example: `snowflakeinc/snowflake-kafka-connector:2.1.2`.

## Configuration

Edit the `connector.properties` file in the root directory to configure your specific connector.

### Example: Snowflake Sink
```properties
name=snowflake-sink-connector
connector.class=com.snowflake.kafka.connector.SnowflakeSinkConnector
tasks.max=1
topics=your-input-topic

# Snowflake connection details
snowflake.url.name=https://your-account.snowflakecomputing.com
snowflake.user.name=your-username
snowflake.private.key=your-private-key
snowflake.database.name=your-database
snowflake.schema.name=your-schema
snowflake.role.name=your-role
```

### Example: PostgreSQL Sink  
```properties
name=postgres-sink-connector
connector.class=io.confluent.connect.jdbc.JdbcSinkConnector
tasks.max=1
topics=your-input-topic
connection.url=jdbc:postgresql://localhost:5432/your_database
connection.user=your_username
connection.password=your_password
auto.create=true
```

**Note:** This template provides the infrastructure; you supply the connection details and credentials specific to your external system.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
