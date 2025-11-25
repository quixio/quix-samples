#!/usr/bin/env python3
import boto3
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
# Note: Upload plain text files for testing
test_data = [
    {"id": 1, "name": "test1", "value": 100},
    {"id": 2, "name": "test2", "value": 200},
    {"id": 3, "name": "test3", "value": 300},
]

for i, record in enumerate(test_data, 1):
    # Create JSON content
    json_content = json.dumps(record).encode('utf-8')

    # Upload to S3
    s3_client.put_object(
        Bucket='test-bucket',
        Key=f'data/data{i}.json',
        Body=json_content,
        ContentType='application/json'
    )
    print(f"Uploaded data{i}.json")

print("MinIO setup complete")
