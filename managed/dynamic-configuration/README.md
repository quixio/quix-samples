# Quix Configuration Manager

The **Quix Configuration Service** offers a web interface and API for managing configurations, retrieve, update, and delete. It supports versioning, metadata, and event notifications via Kafka. Designed for seamless integration with the Quix SDK and platform.

## How to Run

1. Create or log in to your Quix account.
2. Navigate to **Connectors → Add connector → Quix Datalake Sink**.
3. Click **Set up connector**, fill in the required parameters (see below), then click **Test connection & deploy**.

> **Managed Service:**  
> The container image is hosted and operated by Quix. You only provide configuration—no need to manage Docker, servers, or updates.

## Configuration

### Required Configuration

- **topic**: Kafka topic for real-time updates.
- **mongoDatabase**: MongoDB database name
- **mongoCollection**: MongoDB collection name
- **mongoUrlSecret**: MongoDB connection URL (example: `mongo://user:password@mongo:27017`)

### API Configuration

- **port**: HTTP server port (default: `80`)
- **workers**: Number of HTTP worker processes (default: `1`)
- **logLevel**: Logging level (`INFO` or `DEBUG`, default: `INFO`)
- **kafkaFlushTimeout**: Timeout for flushing updates to Kafka (default: `5`)
- **contentStore**: Storage backend for configuration content (`mongo` or `file`, default: `mongo`)
