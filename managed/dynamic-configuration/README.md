# Dynamic Configuration Manager

The **Dynamic Configuration Manager** offers a web interface and API for managing configurations, retrieve, update, and delete. It supports versioning, metadata, and event notifications via Kafka. Designed for seamless integration with the Quix SDK and platform.

## How to Run

1. Create or log in to your Quix account.
2. Navigate to **Connectors → Add connector → Quix Datalake Sink**.
3. Click **Set up connector**, fill in the required parameters (see below), then click **Test connection & deploy**.

> **Managed Service:**  
> The container image is hosted and operated by Quix. You only provide configuration—no need to manage Docker, servers, or updates.

## Configuration

### Required Configuration

- **topic**: Kafka topic for configuration real-time updates.
- **mongoHost**: MongoDB host.
- **mongoPort**: MongoDB port.
- **mongoUser**: MongoDB user.
- **mongoPasswordSecret**: MongoDB password secret.
- **mongoDatabase**: MongoDB database name.
- **mongoCollection**: MongoDB collection name.

### Optional Configuration

- **consumerGroup**: Kafka consumer group identifier (default: `config-api-v1`).
- **port**: HTTP port of the API (default: `80`).
- **workers**: Number of worker processes (default: `1`).
- **contentStore**: Storage backend for configuration content (`mongo` or `file`, default: `mongo`).
