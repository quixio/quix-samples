# Kafka Connect Source

[This template](https://github.com/quixio/quix-samples/tree/main/shell/kafka-connect-source) provides a generic framework for running any Kafka Connect source connector in Quix, allowing you to stream data from external systems (databases, APIs, files) into Kafka topics.

## Getting started

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Templates` tab to use this template.

Then either:
- **Deploy** immediately to your workspace 
- **Customize** to modify the code or configuration before deployment

## Environment variables

The template uses the following environment variables:

- **output**: The name of the output topic to publish the sourced data to.
- **CONNECT_OFFSET_STORAGE_TOPIC**: Topic name to use for storing offsets for Kafka Connect.
- **CONNECT_CONFIG_STORAGE_TOPIC**: Topic name to use for storing connector and task configurations for Kafka Connect.
- **CONNECT_STATUS_STORAGE_TOPIC**: Topic name to use for storing statuses for Kafka Connect.
- **CONNECTOR_NAME**: **(Required)** The [Confluent Hub](https://www.confluent.io/hub) Kafka connector to use. Example: `debezium/debezium-connector-postgresql:2.2.1`.

## How it works

1. **Deploy the template** with your chosen connector from [Confluent Hub](https://www.confluent.io/hub)
2. **Configure the connection** by editing `connector.properties` with your source system credentials
3. **Data flows automatically** from your external source to the Kafka output topic

## Configuration

Edit the `connector.properties` file in the root directory to configure your specific connector.

### Example: Debezium PostgreSQL Source
```properties
name=postgres-source-connector
connector.class=io.debezium.connector.postgresql.PostgresConnector
tasks.max=1

# Database connection
database.hostname=localhost
database.port=5432
database.user=debezium
database.password=debezium
database.dbname=postgres
database.server.name=postgres-server

# Tables to monitor
table.include.list=public.users,public.orders

# Output topic prefix
kafka.topic=postgres-cdc
```

### Example: MongoDB Source
```properties
name=mongodb-source-connector
connector.class=com.mongodb.kafka.connect.MongoSourceConnector
tasks.max=1

# MongoDB connection
connection.uri=mongodb://username:password@localhost:27017/mydb?authSource=admin
database=mydb
collection=users

# Output configuration
topic.prefix=mongodb
output.format.value=json
```

**Note:** This template provides the infrastructure; you supply the connection details and credentials specific to your source system.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
