# Dynamic Configuration Manager

The **Dynamic Configuration Manager** is a managed service to store, version, and distribute application configuration at runtime. It provides a simple REST API and lightweight UI, persists configuration in a backing store, and emits change events to Kafka so services can react immediately. It works great with the Quix platform and SDK, and can be used from any HTTP/Kafka client.

## Key capabilities

- CRUD configuration items with optional metadata
- Versioning and history
- Real-time change notifications on a Kafka topic
- Pluggable content store (Mongo by default; file for simple setups)
- Simple REST API and web UI
- Horizontal scaling via workers
- Optional consumer group for isolated consumption

## How it works (high-level)

1. Create/update requests persist content and produce a new version.
2. The service publishes a change event to the configured Kafka topic.
3. Consumers subscribe to that topic and apply changes

## How to Run

1. Create or log in to your Quix account.
2. Navigate to **Connectors → Add connector → Dynamic Configuration Manager**.
3. Click **Set up connector**, fill in the required parameters (see below), then click **Test connection & deploy**.

> **Managed Service:**  
> The container image is hosted and operated by Quix. You only provide configuration—no need to manage Docker, servers, or updates.

## Configuration

### Required Configuration

- **topic**: Kafka topic for configuration updates.
- **mongoHost**: MongoDB host.
- **mongoPort**: MongoDB port.
- **mongoUser**: MongoDB user.
- **mongoPasswordSecret**: MongoDB password secret.
- **mongoDatabase**: MongoDB database name.
- **mongoCollection**: MongoDB collection name.

### Optional Configuration

- **consumerGroup**: Kafka consumer group identifier (default: `config-api-v1`).
- **port**: Port of the API (default: `80`).
- **workers**: Number of worker processes (default: `1`).
- **contentStore**: Storage backend for configuration content (`mongo` or `file`, default: `mongo`).
