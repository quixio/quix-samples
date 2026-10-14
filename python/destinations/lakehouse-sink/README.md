# Quix Lakehouse Sink

This connector consumes time-series data from a Kafka topic and writes it to blob storage as Hive-partitioned Parquet files, with optional Quix Lakehouse catalog registration for the lakehouse query API.

## Features

- **Multi-Cloud Storage**: Supports AWS S3, Azure Blob Storage, GCP, MinIO via Quix platform blob storage binding
- **Hive Partitioning**: Automatically partition data by any columns (e.g., location, sensor type, year/month/day/hour)
- **Time-based Partitioning**: Extract year/month/day/hour from timestamp columns for efficient time-based queries
- **Virtual Partitions**: Keep high-cardinality ids filterable without fragmenting storage, using a `~` prefix in `HIVE_COLUMNS`
- **Query Performance**: Per-file statistics (zone maps), a recorded sort column for compaction, and configurable Parquet row-group size
- **Quix Lakehouse Catalog Integration**: Optional table registration in a REST Catalog for seamless integration with analytics tools
- **Efficient Batching**: Configurable batch sizes and parallel uploads for high throughput
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

### Data Organization

- **`TABLE_NAME`**: Table name for data organization and registration
  *Default*: Uses the topic name if not specified

- **`HIVE_COLUMNS`**: Comma-separated list of columns for Hive partitioning. Include `year`, `month`, `day`, `hour` to extract from `TIMESTAMP_COLUMN`. Prefix an entry with `~` to make it a *virtual* partition (see below)
  *Example*: `location,year,month,day,~device_id`
  *Default*: `""` (no partitioning)

- **`TIMESTAMP_COLUMN`**: Column containing timestamp values to extract year/month/day/hour from
  *Default*: `ts_ms`

### Query Performance

Requires `quixstreams[quixdatalake]>=3.26.0`.

- **`STATS_COLUMNS`**: Comma-separated columns to compute per-file min/max statistics ("zone maps") for. The query layer uses them to skip files whose value range cannot satisfy a `WHERE` or `ORDER BY`. Statistics are computed from the in-memory batch, so they are nearly free — restrict the list only on very wide tables where per-file, per-column rows get costly in the catalog
  *Example*: `ts_ms,seq`
  *Default*: `""` — statistics for **every** numeric and timestamp column

- **`SORT_COLUMN`**: Column recorded on the table as `properties.sort_column`; lakehouse compaction writes files ordered by it so `ORDER BY` and time-range queries can skip files and stream. This is table metadata only — the sink does **not** reorder rows within a file
  *Example*: `seq`
  *Default*: `""` — falls back to `TIMESTAMP_COLUMN`

- **`ROW_GROUP_ROWS`**: Maximum rows per Parquet row group. A reader pays roughly one storage range request per row group, so many small groups cost a round-trip storm on high-latency storage, while one huge group forfeits intra-file skipping and inflates reader memory. A flush smaller than this is a single row group; only large flushes are split
  *Example*: `250000`
  *Default*: `""` — the sink default of `1000000`, matching lakehouse compaction

#### Virtual partitions

A plain `HIVE_COLUMNS` entry is a **physical** partition: it becomes a real `key=value/` folder,
splits the batch into one file per distinct value, and the column is dropped from the Parquet
because the path already carries it.

An entry prefixed with `~` is a **virtual** partition: it joins the partition tree and stays
filterable, but gets **no** folder, does **not** split files, and the column **stays in** the
Parquet data. Use it for high-cardinality identifiers — device, session, order — where a physical
partition would emit one tiny file per value per batch.

```bash
HIVE_COLUMNS=year,month,day,~device_id
TIMESTAMP_COLUMN=ts_ms
```

Rules:

- No space after the `~`. `~ device_id` creates a virtual column literally named `" device_id"`.
- `year`, `month`, `day` and `hour` are **physical only**. They are derived from
  `TIMESTAMP_COLUMN`, so a virtual `~hour` would mean inventing a column your records never
  contained. Time-range pruning comes from `STATS_COLUMNS` instead.
- A virtual column must be a field your records actually carry — reads rebuild physical columns
  from the folder path, but a virtual column can only come from the Parquet data itself.
- Each data file gets a virtual-index sidecar in a `.vidx/` subfolder of its own partition folder.
  Sidecar writes are best-effort: a failure is logged, never raised, and self-heals on the next
  write.

### Catalog Integration (Optional)

On Quix Cloud, when the workspace has a Lakehouse provisioned, `CATALOG_URL` and `CATALOG_AUTH_TOKEN` are auto-injected by the platform at deployment time. To use a self-hosted catalog or to skip registration, set these as deployment variables on the deployed sink.

- **`AUTO_DISCOVER`**: Automatically register table in REST Catalog on first write
  *Default*: `true`

- **`CATALOG_NAMESPACE`**: Catalog namespace for table registration
  *Default*: `default`

### Kafka Configuration

- **`CONSUMER_GROUP`**: Kafka consumer group name
  *Default*: `s3_direct_sink_v1.0`

- **`AUTO_OFFSET_RESET`**: Where to start consuming if no offset exists
  *Default*: `earliest`
  *Options*: `earliest`, `latest`

- **`KAFKA_KEY_DESERIALIZER`**: The key deserializer to use
  *Default*: `str`

- **`KAFKA_VALUE_DESERIALIZER`**: The value deserializer to use
  *Default*: `json`

### Performance Tuning

- **`BATCH_SIZE`**: Number of messages to batch before writing to storage
  *Default*: `1000`

- **`COMMIT_INTERVAL`**: Kafka commit interval in seconds
  *Default*: `30`

- **`MAX_WRITE_WORKERS`**: How many files can be written in parallel to storage at once
  *Default*: `10`

### Application Settings

- **`LOGLEVEL`**: Set application logging level
  *Default*: `INFO`
  *Options*: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## Blob Storage Configuration

Blob storage is configured through the Quix platform's blob storage binding. When deploying this connector, the platform automatically injects the `Quix__BlobStorage__Connection__Json` environment variable with your storage credentials.

Supported storage providers:
- AWS S3
- Azure Blob Storage
- Google Cloud Storage
- MinIO
- Other S3-compatible storage

## Partitioning Strategy Examples

### Example 1: Time-based partitioning
```bash
HIVE_COLUMNS=year,month,day
TIMESTAMP_COLUMN=ts_ms
```
Creates: `{workspace}/data-lake/time-series/{table}/year=2024/month=01/day=15/data_*.parquet`

### Example 2: Multi-dimensional partitioning
```bash
HIVE_COLUMNS=location,sensor_type,year,month
TIMESTAMP_COLUMN=timestamp
```
Creates: `{workspace}/data-lake/time-series/{table}/location=NYC/sensor_type=temp/year=2024/month=01/data_*.parquet`

### Example 3: No partitioning
```bash
HIVE_COLUMNS=
```
Creates: `{workspace}/data-lake/time-series/{table}/data_*.parquet`

### Example 4: Virtual partition for a high-cardinality id
```bash
HIVE_COLUMNS=year,month,day,~device_id
TIMESTAMP_COLUMN=ts_ms
```
Creates:
```
{workspace}/data-lake/time-series/{table}/year=2024/month=01/day=15/data_*.parquet        # every device, one file
{workspace}/data-lake/time-series/{table}/year=2024/month=01/day=15/.vidx/data_*.parquet   # virtual index
```
`device_id` has no folder and does not split files, but it stays in the Parquet data, so
`WHERE device_id = 'sensor-42'` still resolves.

## Changing an existing table

Table properties are written **once, at table creation**. On restart against a table that is
already registered in the catalog, the sink logs `Table '<name>' already exists in catalog` and
returns early — so changing `SORT_COLUMN` or `TIMESTAMP_COLUMN` on an existing table is
**silently ignored**, and the original metadata stands. Changing the set of physical
`HIVE_COLUMNS` is worse than ignored: it raises at startup, because the configured partitions no
longer match the folders already on disk (and the spec already registered in the catalog).

**Any layout or table-property change means a NEW TABLE NAME.** Give the table a version suffix
(`sensor_readings_v1` → `sensor_readings_v2`) and re-sink, the same way consumer groups are
versioned. `STATS_COLUMNS` and `ROW_GROUP_ROWS` are the two exceptions — they are per-file
settings, not table properties, so they can be changed freely on a live table and take effect on
the next flush.

## Architecture

The sink uses a batching architecture for high throughput:

1. **Consume**: Messages are consumed from Kafka in batches
2. **Transform**: Time-based columns are extracted if needed
3. **Partition**: Data is grouped by partition columns
4. **Upload**: Multiple files are uploaded to storage in parallel
5. **Register**: Files are registered in the catalog (if configured)

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.
