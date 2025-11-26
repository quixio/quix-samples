import boto3
import os
import sys
import time
import json

def main():
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    bucket_name = os.getenv("S3_BUCKET", "test-bucket")
    prefix = os.getenv("S3_PREFIX", "test_data")

    print(f"Connecting to MinIO at {minio_endpoint}")

    # Create S3 client for MinIO
    s3_client = boto3.client(
        's3',
        endpoint_url=f'http://{minio_endpoint}',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='us-east-1'
    )

    expected_count = 1  # Expecting at least 1 file
    max_attempts = 20
    found_files = []

    print(f"Checking S3 bucket '{bucket_name}' with prefix '{prefix}' for files...")

    # Retry logic with polling
    for attempt in range(max_attempts):
        found_files = []

        try:
            # List objects in the bucket with the prefix
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )

            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    # Skip directory markers
                    if not key.endswith('/'):
                        found_files.append(key)
                        print(f"Found file: {key} (size: {obj['Size']} bytes)")

        except Exception as e:
            print(f"Error listing objects: {e}")

        if len(found_files) >= expected_count:
            print(f"\nSuccess: Found {len(found_files)} file(s) in S3")

            # Verify the file(s) contain valid data
            try:
                all_records = []

                # Read all files and collect records
                for file_key in found_files:
                    print(f"\nReading file: {file_key}")

                    obj_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
                    content = obj_response['Body'].read().decode('utf-8')

                    print(f"File size: {len(content)} bytes")
                    print(f"File content (first 1000 chars):\n{content[:1000]}")
                    print(f"---")

                    if file_key.endswith('.json') or file_key.endswith('.jsonl'):
                        lines = content.strip().split('\n')
                        print(f"File contains {len(lines)} line(s)")

                        for idx, line in enumerate(lines):
                            if line.strip():
                                print(f"Parsing line {idx}: {line[:100]}...")
                                try:
                                    data = json.loads(line)
                                    all_records.append(data)
                                    print(f"✓ Successfully parsed record: {data}")
                                except json.JSONDecodeError as je:
                                    print(f"ERROR: Invalid JSON on line {idx}: {je}")
                                    print(f"Line content: {line}")
                                    sys.exit(1)
                    else:
                        print(f"WARNING: Skipping non-JSON file: {file_key}")

                print(f"\nTotal records found: {len(all_records)}")

                # Verify we have the expected number of records
                expected_message_count = int(os.getenv("TEST_MESSAGE_COUNT", "3"))
                if len(all_records) < expected_message_count:
                    print(f"ERROR: Expected {expected_message_count} records, found {len(all_records)}")
                    sys.exit(1)

                # Verify each record has the expected structure and values
                expected_metadata_fields = {'_key', '_timestamp', '_value'}
                expected_value_fields = {'id', 'name', 'value', 'timestamp'}
                found_ids = set()

                for i, record in enumerate(all_records):
                    print(f"\nValidating record {i}: {record}")

                    # Check for Kafka metadata fields
                    actual_fields = set(record.keys())
                    if not expected_metadata_fields.issubset(actual_fields):
                        missing = expected_metadata_fields - actual_fields
                        print(f"ERROR: Record {i} missing metadata fields: {missing}")
                        sys.exit(1)

                    # Extract the actual message value
                    message_value = record['_value']
                    if not isinstance(message_value, dict):
                        print(f"ERROR: Record {i} _value is not a dict: {type(message_value)}")
                        sys.exit(1)

                    # Check for required fields in _value
                    actual_value_fields = set(message_value.keys())
                    if not expected_value_fields.issubset(actual_value_fields):
                        missing = expected_value_fields - actual_value_fields
                        print(f"ERROR: Record {i} _value missing fields: {missing}")
                        sys.exit(1)

                    # Verify id is an integer
                    if not isinstance(message_value['id'], int):
                        print(f"ERROR: Record {i} has invalid id type: {type(message_value['id'])}")
                        sys.exit(1)

                    found_ids.add(message_value['id'])

                    # Verify _key matches expected pattern
                    expected_key = f"key_{message_value['id']}"
                    if record['_key'] != expected_key:
                        print(f"ERROR: Record {i} has incorrect _key. Expected '{expected_key}', got '{record['_key']}'")
                        sys.exit(1)

                    # Verify name matches expected pattern
                    expected_name = f"test_item_{message_value['id']}"
                    if message_value['name'] != expected_name:
                        print(f"ERROR: Record {i} has incorrect name. Expected '{expected_name}', got '{message_value['name']}'")
                        sys.exit(1)

                    # Verify value matches expected pattern
                    expected_value = f"test_value_{message_value['id']}"
                    if message_value['value'] != expected_value:
                        print(f"ERROR: Record {i} has incorrect value. Expected '{expected_value}', got '{message_value['value']}'")
                        sys.exit(1)

                    print(f"✓ Record {i} validated: _key={record['_key']}, id={message_value['id']}, name={message_value['name']}, value={message_value['value']}")

                # Verify we got all expected IDs (0, 1, 2)
                expected_ids = set(range(expected_message_count))
                if found_ids != expected_ids:
                    print(f"ERROR: Missing IDs. Expected {expected_ids}, found {found_ids}")
                    sys.exit(1)

                print(f"\n✓ All {len(all_records)} records validated successfully")
                print(f"✓ All expected IDs present: {sorted(found_ids)}")

            except Exception as e:
                print(f"ERROR: Failed to verify file content: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)

            sys.exit(0)

        print(f"Attempt {attempt + 1}/{max_attempts}: Found {len(found_files)} file(s), waiting...")
        time.sleep(2)

    print(f"\nFAILED: Only found {len(found_files)} file(s) after {max_attempts} attempts")
    sys.exit(1)

if __name__ == "__main__":
    main()
