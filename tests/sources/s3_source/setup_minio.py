#!/usr/bin/env python3
import boto3
import gzip
import json
from botocore.client import Config

# MinIO configuration
s3_client = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# Create bucket
try:
    s3_client.create_bucket(Bucket='test-bucket')
    print("Bucket created successfully")
except Exception as e:
    print(f"Bucket might already exist: {e}")

# Upload test data
# Note: Each file contains one JSON object per line (JSONL format)
test_data = [
    [{"id": 1, "name": "test1", "value": 100}],
    [{"id": 2, "name": "test2", "value": 200}],
    [{"id": 3, "name": "test3", "value": 300}],
]

for i, records in enumerate(test_data, 1):
    # Create JSONL content (one JSON per line)
    jsonl_content = '\n'.join(json.dumps(record) for record in records).encode('utf-8')
    gzipped_content = gzip.compress(jsonl_content)

    # Upload to S3
    s3_client.put_object(
        Bucket='test-bucket',
        Key=f'data/data{i}.json.gz',
        Body=gzipped_content
    )
    print(f"Uploaded data{i}.json.gz")

print("MinIO setup complete")
