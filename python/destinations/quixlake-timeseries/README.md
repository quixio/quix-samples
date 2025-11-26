# Quix TS Datalake Sink

This connector consumes time-series data from a Kafka topic and writes it to S3 as Hive-partitioned Parquet files, with optional Quix catalog registration for data lake query API.

## Features

- **Hive Partitioning**: Automatically partition data by any columns (e.g., location, sensor type, year/month/day/hour)
- **Time-based Partitioning**: Extract year/month/day/hour from timestamp columns for efficient time-based queries
- **Quix Catalog Integration**: Optional table registration in a REST Catalog for seamless integration with analytics tools
- **Efficient Batching**: Configurable batch sizes and parallel S3 uploads for high throughput
- **Schema Evolution**: Automatic schema detection from data
- **Partition Validation**: Prevents data corruption by validating partition strategies against existing tables

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?xlink=github) account or log in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either:
* Click `Test connection & deploy` to deploy the pre-built and configured container into Quix
* Or click `Customise connector` to inspect or alter the code before deployment

## Environment Variables

### Required

- **`input`**: Name of the Kafka input topic to consume from
  *Default*: `sensor-data`

- **`S3_BUCKET`**: S3 bucket name for storing Parquet files

### S3 Configuration

- **`S3_PREFIX`**: S3 prefix/path for data files
  *Default*: `data`

- **`AWS_ACCESS_KEY_ID`**: AWS Access Key ID for S3 access
  *Default*: `""` (uses IAM role if empty)

- **`AWS_SECRET_ACCESS_KEY`**: AWS Secret Access Key for S3 access
  *Default*: `""` (uses IAM role if empty)

- **`AWS_REGION`**: AWS region for S3 bucket
  *Default*: `us-east-1`

- **`AWS_ENDPOINT_URL`**: Custom S3 endpoint URL for non-AWS S3-compatible storage
  *Examples*:
  - MinIO: `http://minio.example.com:9000`
  - Wasabi: `https://s3.wasabisys.com`
  - DigitalOcean Spaces: `https://nyc3.digitaloceanspaces.com`
  - Backblaze B2: `https://s3.us-west-004.backblazeb2.com`
  *Default*: None (uses AWS S3)

### Data Organization

- **`TABLE_NAME`**: Table name for data organization and registration
  *Default*: Uses the topic name if not specified

- **`HIVE_COLUMNS`**: Comma-separated list of columns for Hive partitioning. Include `year`, `month`, `day`, `hour` to extract from `TIMESTAMP_COLUMN`
  *Example*: `location,year,month,day,sensor_type`
  *Default*: `""` (no partitioning)

- **`TIMESTAMP_COLUMN`**: Column containing timestamp values to extract year/month/day/hour from
  *Default*: `ts_ms`

### Catalog Integration (Optional)

- **`CATALOG_URL`**: REST Catalog URL for optional table registration (leave empty to skip)
  *Example*: `https://catalog.example.com/api/v1`

- **`CATALOG_AUTH_TOKEN`**: If using a catalog, the respective auth token to access it

- **`AUTO_DISCOVER`**: Automatically register table in REST Catalog on first write
  *Default*: `true`

- **`CATALOG_NAMESPACE`**: Catalog namespace for table registration
  *Default*: `default`

### Kafka Configuration

- **`CONSUMER_GROUP`**: Kafka consumer group name
  *Default*: `s3_direct_sink_v1.0`

- **`AUTO_OFFSET_RESET`**: Where to start consuming if no offset exists
  *Default*: `latest`
  *Options*: `earliest`, `latest`

- **`KAFKA_KEY_DESERIALIZER`**: The key deserializer to use
  *Default*: `str`

- **`KAFKA_VALUE_DESERIALIZER`**: The value deserializer to use
  *Default*: `json`

### Performance Tuning

- **`BATCH_SIZE`**: Number of messages to batch before writing to S3
  *Default*: `1000`

- **`COMMIT_INTERVAL`**: Kafka commit interval in seconds
  *Default*: `30`

- **`MAX_WRITE_WORKERS`**: How many files can be written in parallel to S3 at once
  *Default*: `10`

### Application Settings

- **`LOGLEVEL`**: Set application logging level
  *Default*: `INFO`
  *Options*: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## Partitioning Strategy Examples

### Example 1: Time-based partitioning
```bash
HIVE_COLUMNS=year,month,day
TIMESTAMP_COLUMN=ts_ms
```
Creates: `s3://bucket/prefix/table/year=2024/month=01/day=15/data_*.parquet`

### Example 2: Multi-dimensional partitioning
```bash
HIVE_COLUMNS=location,sensor_type,year,month
TIMESTAMP_COLUMN=timestamp
```
Creates: `s3://bucket/prefix/table/location=NYC/sensor_type=temp/year=2024/month=01/data_*.parquet`

### Example 3: No partitioning
```bash
HIVE_COLUMNS=
```
Creates: `s3://bucket/prefix/table/data_*.parquet`

## Using Non-AWS S3-Compatible Storage

This connector supports any S3-compatible storage service by setting the `AWS_ENDPOINT_URL` environment variable.

### MinIO Example
```bash
AWS_ENDPOINT_URL=http://minio.example.com:9000
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_REGION=us-east-1
S3_BUCKET=my-data-lake
```

### Wasabi Example
```bash
AWS_ENDPOINT_URL=https://s3.wasabisys.com
AWS_ACCESS_KEY_ID=your-wasabi-access-key
AWS_SECRET_ACCESS_KEY=your-wasabi-secret-key
AWS_REGION=us-east-1
S3_BUCKET=my-data-lake
```

### DigitalOcean Spaces Example
```bash
AWS_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
AWS_ACCESS_KEY_ID=your-spaces-access-key
AWS_SECRET_ACCESS_KEY=your-spaces-secret-key
AWS_REGION=nyc3
S3_BUCKET=my-data-lake
```

### Backblaze B2 Example
```bash
AWS_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com
AWS_ACCESS_KEY_ID=your-b2-key-id
AWS_SECRET_ACCESS_KEY=your-b2-application-key
AWS_REGION=us-west-004
S3_BUCKET=my-data-lake
```

## Architecture

The sink uses a batching architecture for high throughput:

1. **Consume**: Messages are consumed from Kafka in batches
2. **Transform**: Time-based columns are extracted if needed
3. **Partition**: Data is grouped by partition columns
4. **Upload**: Multiple files are uploaded to S3 in parallel
5. **Register**: Files are registered in the catalog (if configured)

## Requirements

- S3 bucket access:
  - AWS S3, or
  - Any S3-compatible storage (MinIO, Wasabi, DigitalOcean Spaces, Backblaze B2, etc.)
- Optional: Quix REST Catalog endpoint for data catalog integration

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
