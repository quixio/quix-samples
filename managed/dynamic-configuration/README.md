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

This service can leverage a blob storage configured on our platform (see [blob storage docs](https://quix.io/docs/quix-cloud/managed-services/blob-storage.html) for setup instructions).

The blob storage configuration is automatically injected only when `contentStore` is set to `file`.

## Learn More

For complete details, check our [official documentation](https://quix.io/docs/quix-cloud/managed-services/dynamic-configuration.html).

## Using with Quix Streams join_lookup

The Dynamic Configuration Manager works seamlessly with Quix Streams' `join_lookup` feature to enrich streaming data with configuration data in real-time.

### Basic Example

Here's how to use Dynamic Configuration with `join_lookup` to enrich sensor data with device configurations:

```python
from quixstreams import Application
from quixstreams.dataframe.joins.lookups import QuixConfigurationService

# Initialize the application
app = Application()

# Create a lookup instance pointing to your configuration topic
lookup = QuixConfigurationService(
    topic=app.topic("device-configurations"),
    app_config=app.config
)

# Create your main data stream
sdf = app.dataframe(app.topic("sensor-data"))

# Enrich sensor data with device configuration
sdf = sdf.join_lookup(
    lookup=lookup,
    on="device_id",  # The field to match on
    fields={
        "device_name": lookup.json_field(
            jsonpath="$.device.name",
            type="device-config"
        ),
        "calibration_params": lookup.json_field(
            jsonpath="$.calibration",
            type="device-config"
        ),
        "firmware_version": lookup.json_field(
            jsonpath="$.firmware.version",
            type="device-config"
        )
    }
)

# Process the enriched data
sdf = sdf.apply(lambda value: {
    **value,
    "device_info": f"{value['device_name']} (v{value['firmware_version']})"
})

# Output to destination topic
sdf.to_topic(app.topic("enriched-sensor-data"))

if __name__ == "__main__":
    app.run()
```

### Advanced Configuration Matching

You can also use custom key matching logic for more complex scenarios:

```python
def custom_key_matcher(value, key):
    """Custom logic to determine configuration key"""
    device_type = value.get("device_type", "unknown")
    location = value.get("location", "default")
    return f"{device_type}-{location}"

# Use custom key matching
sdf = sdf.join_lookup(
    lookup=lookup,
    on=custom_key_matcher,
    fields={
        "config": lookup.json_field(
            jsonpath="$",
            type="location-config"
        )
    }
)
```

### Binary Configuration Support

For non-JSON configurations (firmware files, calibration data, etc.):

```python
sdf = sdf.join_lookup(
    lookup=lookup,
    on="device_id",
    fields={
        "firmware_binary": lookup.bytes_field(
            type="firmware"
        ),
        "calibration_data": lookup.bytes_field(
            type="calibration"
        )
    }
)
```

### How It Works

1. **Configuration Updates**: When configurations are updated via the Dynamic Configuration API, lightweight Kafka events are published to your configuration topic.

2. **Real-time Enrichment**: The `join_lookup` feature listens to these events, fetches the latest configuration content, and caches it locally.

3. **Stream Enrichment**: As your main data stream processes records, `join_lookup` automatically enriches each record with the appropriate configuration data based on the matching key and timestamp.

4. **Version Management**: The system automatically handles configuration versioning, ensuring that each record is enriched with the configuration version that was valid at the time the record was created.

### Benefits

- **Real-time Updates**: Configuration changes are immediately available to your streaming applications
- **Large File Support**: Handle configuration files too large for direct Kafka streaming
- **Version Control**: Automatic versioning ensures data consistency
- **Performance**: Local caching minimizes API calls and latency
- **Flexibility**: Support for both JSON and binary configuration content
