# QuixLake S3 Destination

[This connector](https://github.com/quixio/quix-samples/tree/main/python/destinations/quixlake-destination) demonstrates how to consume data from a Kafka topic and write it directly to S3 in Parquet format, with optional registration in the QuixLake catalog.

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Environment Variables

The connector uses the following environment variables:

- **input**: Name of the Kafka input topic to consume from (Default: `sensor-data`, Required: `True`)
- **S3_BUCKET**: S3 bucket name for storing Parquet files (Required: `True`)
- **S3_PREFIX**: S3 prefix/path for data files (Default: `data`, Required: `False`)
- **TABLE_NAME**: Table name for data organization and registration (Default: `data`, Required: `False`)
- **HIVE_COLUMNS**: Comma-separated list of columns for Hive partitioning (e.g., location,sensor_type) (Default: ``, Required: `False`)
- **TIMESTAMP_COLUMN**: Column containing timestamp values for time-based partitioning (Default: `ts_ms`, Required: `False`)
- **TIMESTAMP_FORMAT**: Time partition granularity (Default: `day`, Required: `False`)
- **QUIXLAKE_API_URL**: QuixLake API URL for optional table registration (leave empty to skip) (Default: `http://quixlake-api`, Required: `False`)
- **AUTO_DISCOVER**: Automatically register table in QuixLake catalog on first write (Default: `true`, Required: `False`)
- **BATCH_SIZE**: Number of messages to batch before writing to S3 (Default: `1000`, Required: `False`)
- **COMMIT_INTERVAL**: Kafka commit interval in seconds (Default: `30`, Required: `False`)
- **CONSUMER_GROUP**: Kafka consumer group name (Default: `s3_direct_sink_v1.0`, Required: `False`)
- **AUTO_OFFSET_RESET**: Where to start consuming if no offset exists (Default: `latest`, Required: `False`)
- **AWS_ACCESS_KEY_ID**: AWS Access Key ID for S3 access (Required: `False`)
- **AWS_SECRET_ACCESS_KEY**: AWS Secret Access Key for S3 access (Required: `False`)
- **AWS_REGION**: AWS region for S3 bucket (Default: `us-east-1`, Required: `False`)

## Requirements / Prerequisites

You will need:
- An AWS account with S3 bucket access
- AWS Access Key ID and Secret Access Key with appropriate permissions
- A configured S3 bucket in your specified region

## Features

- Direct S3 writing with DuckDB for high performance
- Automatic schema discovery from Kafka messages
- Hive-style partitioning support
- Time-based partitioning (year/month/day/hour)
- Automatic table registration in QuixLake catalog
- Efficient batching and commit handling

## Query your data

### Using DuckDB

You can query your data directly from S3 using DuckDB:

```python
import duckdb

# Connect to DuckDB
conn = duckdb.connect()

# Configure S3 credentials
conn.execute(f"""
    SET s3_access_key_id = 'YOUR_ACCESS_KEY';
    SET s3_secret_access_key = 'YOUR_SECRET_KEY';
    SET s3_region = 'YOUR_REGION';
""")

# Query data directly from S3
result = conn.execute("""
    SELECT * FROM read_parquet('s3://your-bucket/data/*/*/*.parquet')
    LIMIT 10
""").fetchall()

print(result)
```

### Using AWS Athena

If you prefer to use AWS Athena, you can create an external table:

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS your_table_name (
    -- Define your columns here based on your data schema
)
STORED AS PARQUET
LOCATION 's3://your-bucket/data/'
```

Then query using standard SQL:

```sql
SELECT * FROM your_table_name LIMIT 10;
```

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.