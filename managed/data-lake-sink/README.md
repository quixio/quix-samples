# Quix Datalake Sink

The **Quix Datalake Sink** is a managed service for seamless data ingestion into the Quix Data Lake. It offers a robust, extensible, and user-friendly interface for building efficient and reliable data pipelines for analytics and machine learning.

## How to Run

1. Create or log in to your Quix account.
2. Navigate to **Connectors → Add connector → Quix Datalake Sink**.
3. Click **Set up connector**, fill in the required parameters (see below), then click **Test connection & deploy**.

> **Managed Service:**  
> The container image is hosted and operated by Quix. You only provide configuration—no need to manage Docker, servers, or updates.

## Configuration

### Required Configuration

- **topic**: The Kafka topic to consume (**required**)

### Quix Streams Configuration

This connector uses [quixstreams](https://github.com/quixio/quix-streams) and exposes several parameters from the library. For more details, see the [Quix Streams documentation](https://quix.io/docs/quix-streams/configuration.html#advanced-kafka-configuration).

- **commitTimeInterval**: Seconds between commits (default: `60`)
- **commitMsgInterval**: Messages between commits (default: `0`)
- **consumerGroup**: Kafka consumer group ID (default: `quixstreams-default`)
- **autoOffsetReset**: Offset reset strategy (`latest` or `earliest`, default: `latest`)

### Datalake-Specific Configuration

These parameters are unique to the Quix Datalake Sink:

- **avroCompression**: Avro compression codec (`snappy` or `gzip`, default: `snappy`)
- **maxWorkers**: Maximum number of threads for uploading (default: `5`)
- **indexRowCount**: Number of checkpoints per index file (default: `1000`)
- **datacatalogRequestTimeout**: Data Catalog API timeout in seconds (default: `5`)
- **logLevel**: Logging level (`INFO` or `DEBUG`, default: `INFO`)

### Blob Storage

This service can leverage blob storage configured on our platform (see [blob storage docs](https://quix.io/docs/deploy/blob-storage.html) for setup instructions).
