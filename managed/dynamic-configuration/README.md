# Dynamic Configuration Manager

The **Dynamic Configuration Manager** is a managed service for handling
**large, versioned configuration files** related to devices, sensors, or
physical assets.
These configurations often change in real time (e.g., updates to
equipment parameters, IoT sensor mappings, or lab/test system setups),
but are **too large to send through Kafka directly**.

Instead of streaming entire configuration payloads, the service:

- Stores configurations centrally and versions them.
- Publishes a **lightweight Kafka event** with only the URL, version,
and timestamp of the new configuration.
- Works together with the **Quix Streams SDK**, which will
fetch, cache, and enrich data streams with the appropriate configuration
values.

## Key Capabilities

- Stores and versions large configuration files (JSON or Binary).
- Emits lightweight **Kafka change events** (URL + timestamp +
  version).
- Enables **real-time enrichment** of data streams without sending
  configs through Kafka.
- Designed for **physical asset/device configurations**.
- Provides a simple REST API and embedded UI for browsing/editing
  configs.
- Supports multiple content stores: Mongo (default) or blob/object
  storage (file mode).
- Works seamlessly with the Quix Streams SDK to fetch, cache, and join configs with live data.

## How It Works (High-Level)

1. A new or updated configuration is **persisted and versioned** in the
   service.
2. The service publishes a **Kafka event** containing metadata (URL,
   timestamp, version).
3. Quix Streams SDK consumers subscribe to the topic using join_lookup feature.
4. **Quix Streams SDK downloads the config changes from the API** in realtime, caches it locally, and joins it with incoming data streams using JSONPath or custom join logic.

This design makes it possible to use very large configuration files in
real time without pushing them directly through Kafka.

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

### Blob Storage

This service can leverage blob storage configured on our platform (see [blob storage docs](https://quix.io/docs/deploy/blob-storage.html) for setup instructions).

The blob storage configuration is automatically injected only when `contentStore` is set to `file`.

## Learn More

For complete details, check our [official documentation](https://quix.io/docs/quix-cloud/managed-services/dynamic-configuration.html).
