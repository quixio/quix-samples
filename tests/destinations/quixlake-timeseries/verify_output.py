"""
Verify output for Quix Lake Timeseries destination tests.

Validates that:
1. Parquet files are written to S3 with correct Hive partitioning
2. Data integrity is maintained
3. Partition structure matches configuration
4. All expected records are present
"""
import boto3
import os
import sys
import time
import pyarrow.parquet as pq
from io import BytesIO


def parse_partition_from_path(path, table_name):
    """
    Extract partition values from Hive-style S3 path.

    Example: prefix/table_name/year=2024/month=01/day=15/file.parquet
    Returns: {'year': '2024', 'month': '01', 'day': '15'}
    """
    partitions = {}

    # Find the table name in the path and process everything after it
    if table_name in path:
        parts = path.split(f"{table_name}/", 1)
        if len(parts) > 1:
            partition_path = parts[1]
            # Split by '/' and look for key=value pairs
            for part in partition_path.split('/'):
                if '=' in part and not part.endswith('.parquet'):
                    key, value = part.split('=', 1)
                    partitions[key] = value

    return partitions


def main():
    # Configuration from environment
    minio_endpoint = os.getenv("AWS_ENDPOINT_URL", "http://minio:9000")
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
    bucket_name = os.getenv("S3_BUCKET", "test-bucket")
    s3_prefix = os.getenv("S3_PREFIX", "data")
    table_name = os.getenv("TABLE_NAME", "test-quixlake-input")
    hive_columns = os.getenv("HIVE_COLUMNS", "location,year,month,day")
    expected_message_count = int(os.getenv("TEST_MESSAGE_COUNT", "10"))

    print(f"Configuration:")
    print(f"  Endpoint: {minio_endpoint}")
    print(f"  Bucket: {bucket_name}")
    print(f"  Prefix: {s3_prefix}")
    print(f"  Table: {table_name}")
    print(f"  Expected partitions: {hive_columns}")
    print(f"  Expected messages: {expected_message_count}")

    # Parse expected partition columns
    expected_partition_columns = [col.strip() for col in hive_columns.split(',') if col.strip()]

    # Create S3 client
    print(f"\nConnecting to S3 at {minio_endpoint}...")
    s3_client = boto3.client(
        's3',
        endpoint_url=minio_endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='us-east-1'
    )

    # Build the full table prefix
    table_prefix = f"{s3_prefix}/{table_name}/"

    max_attempts = 45  # 45 attempts * 2s = 90s max wait for CI environments
    found_files = []

    print(f"\nLooking for Parquet files in s3://{bucket_name}/{table_prefix}")

    # Retry logic with polling
    for attempt in range(max_attempts):
        found_files = []

        try:
            # List all objects under the table prefix
            paginator = s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix=table_prefix)

            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        key = obj['Key']
                        # Only include .parquet files (skip directory markers)
                        if key.endswith('.parquet'):
                            found_files.append(key)
                            print(f"Found file: {key} (size: {obj['Size']} bytes)")

        except Exception as e:
            print(f"Error listing objects: {e}")

        if len(found_files) > 0:
            print(f"\n✓ Found {len(found_files)} Parquet file(s)")
            break

        print(f"Attempt {attempt + 1}/{max_attempts}: No files found yet, waiting...")
        time.sleep(2)

    if len(found_files) == 0:
        print(f"\n✗ FAILED: No Parquet files found after {max_attempts} attempts")
        sys.exit(1)

    # Validate partition structure
    print("\n--- Validating Partition Structure ---")
    partition_paths = set()

    for file_key in found_files:
        partitions = parse_partition_from_path(file_key, table_name)

        if expected_partition_columns:
            # Verify all expected partition columns are present
            actual_columns = set(partitions.keys())
            expected_columns = set(expected_partition_columns)

            if actual_columns != expected_columns:
                print(f"✗ ERROR: Partition mismatch in {file_key}")
                print(f"  Expected columns: {expected_columns}")
                print(f"  Actual columns: {actual_columns}")
                sys.exit(1)

            # Build partition path string for tracking unique partitions
            partition_path = "/".join([f"{col}={partitions[col]}" for col in expected_partition_columns])
            partition_paths.add(partition_path)
            print(f"✓ Valid partition: {partition_path}")
        else:
            # No partitioning expected
            if partitions:
                print(f"✗ ERROR: Found unexpected partitions in {file_key}: {partitions}")
                sys.exit(1)
            print(f"✓ No partitioning (as expected)")

    print(f"\n✓ All partition structures valid")
    if partition_paths:
        print(f"✓ Found {len(partition_paths)} unique partition(s):")
        for path in sorted(partition_paths):
            print(f"  - {path}")

    # Read and validate Parquet data
    print("\n--- Validating Parquet Data ---")
    all_records = []

    for file_key in found_files:
        print(f"\nReading: {file_key}")

        try:
            # Download Parquet file
            obj_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            parquet_bytes = obj_response['Body'].read()

            # Read Parquet file with pyarrow
            parquet_file = pq.read_table(BytesIO(parquet_bytes))

            # Convert to list of dictionaries
            records = parquet_file.to_pylist()

            print(f"  Records in file: {len(records)}")
            print(f"  Columns: {parquet_file.schema.names}")

            all_records.extend(records)

            # Show first record as sample
            if records:
                print(f"  Sample record: {records[0]}")

        except Exception as e:
            print(f"✗ ERROR reading Parquet file {file_key}: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    print(f"\n✓ Successfully read {len(all_records)} total records from {len(found_files)} file(s)")

    # Validate record count
    if len(all_records) < expected_message_count:
        print(f"✗ ERROR: Expected at least {expected_message_count} records, found {len(all_records)}")
        sys.exit(1)

    print(f"✓ Record count matches expectation ({len(all_records)} >= {expected_message_count})")

    # Validate record structure and content
    print("\n--- Validating Record Content ---")

    # Partition columns are stored in the directory structure (Hive-style), not in the data
    # So we exclude them from expected fields in the Parquet files
    all_expected_fields = {'id', 'location', 'sensor_type', 'value', 'ts_ms', 'status', 'metadata', '__key'}
    expected_fields = all_expected_fields - set(expected_partition_columns)

    print(f"Expected fields in Parquet data: {expected_fields}")
    print(f"Partition columns (in path only): {expected_partition_columns}")

    found_ids = set()

    for i, record in enumerate(all_records[:expected_message_count]):  # Check first N records
        # Verify required fields exist
        actual_fields = set(record.keys())
        missing_fields = expected_fields - actual_fields

        if missing_fields:
            print(f"✗ ERROR: Record {i} missing fields: {missing_fields}")
            print(f"  Record: {record}")
            sys.exit(1)

        # Verify field types
        if not isinstance(record['id'], int):
            print(f"✗ ERROR: Record {i} 'id' is not an integer: {type(record['id'])}")
            sys.exit(1)

        if not isinstance(record['value'], (int, float)):
            print(f"✗ ERROR: Record {i} 'value' is not numeric: {type(record['value'])}")
            sys.exit(1)

        # ts_ms might be datetime after pyarrow conversion, check for both
        if not isinstance(record['ts_ms'], (int, float)) and not hasattr(record['ts_ms'], 'timestamp'):
            print(f"✗ ERROR: Record {i} 'ts_ms' is not a valid timestamp type: {type(record['ts_ms'])}")
            sys.exit(1)

        # Track IDs
        found_ids.add(record['id'])

        if i < 3:  # Show first 3 records
            print(f"✓ Record {i}: id={record['id']}, "
                  f"sensor_type={record['sensor_type']}, value={record['value']}")

    # Verify we have all expected IDs (0 through expected_message_count - 1)
    expected_ids = set(range(expected_message_count))
    if found_ids != expected_ids:
        print(f"✗ ERROR: Missing or extra IDs")
        print(f"  Expected: {sorted(expected_ids)}")
        print(f"  Found: {sorted(found_ids)}")
        missing = expected_ids - found_ids
        extra = found_ids - expected_ids
        if missing:
            print(f"  Missing: {sorted(missing)}")
        if extra:
            print(f"  Extra: {sorted(extra)}")
        sys.exit(1)

    print(f"\n✓ All {len(all_records)} records validated successfully")
    print(f"✓ All expected IDs present: {sorted(found_ids)[:5]}...{sorted(found_ids)[-2:]}")

    # Validate time-based partitioning if year/month/day columns are used
    if 'year' in expected_partition_columns:
        print("\n--- Validating Time-based Partitioning ---")

        # Check that partition values match the expected date (2024-01-15)
        expected_year = "2024"
        expected_month = "01"
        expected_day = "15"

        for file_key in found_files:
            partitions = parse_partition_from_path(file_key, table_name)

            if 'year' in partitions and partitions['year'] != expected_year:
                print(f"✗ ERROR: Unexpected year in {file_key}: {partitions['year']} (expected {expected_year})")
                sys.exit(1)

            if 'month' in partitions and partitions['month'] != expected_month:
                print(f"✗ ERROR: Unexpected month in {file_key}: {partitions['month']} (expected {expected_month})")
                sys.exit(1)

            if 'day' in partitions and partitions['day'] != expected_day:
                print(f"✗ ERROR: Unexpected day in {file_key}: {partitions['day']} (expected {expected_day})")
                sys.exit(1)

        print(f"✓ All time-based partitions match expected date: {expected_year}-{expected_month}-{expected_day}")

    print("\n" + "="*60)
    print("✓ ALL VALIDATIONS PASSED")
    print("="*60)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
