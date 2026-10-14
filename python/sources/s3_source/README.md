# S3 Configuration File Source

A Quix Streams source service that monitors Amazon S3 buckets for configuration files and streams their content to Kafka topics for processing.

## Overview

This service continuously monitors a specified S3 bucket and folder path for new configuration files. When files are detected, it downloads and publishes their content to the `s3-data` Kafka topic for downstream processing by the XML-to-JSON transformer.

## Features

- **File Monitoring**: Continuous polling of S3 bucket for new files
- **Compression Support**: Handles gzip-compressed files automatically
- **Format Support**: Primarily designed for XML configuration files
- **State Management**: Tracks processed files to avoid duplicates
- **Error Handling**: Robust error handling for S3 connectivity issues
- **Configurable Polling**: Adjustable polling interval for monitoring

## How it Works

1. **Monitoring**: Polls the specified S3 bucket/folder at regular intervals
2. **File Detection**: Identifies new or modified files since last check
3. **Download**: Retrieves file content from S3
4. **Decompression**: Automatically handles gzip decompression if needed
5. **Publishing**: Sends file content to Kafka topic for processing
6. **State Tracking**: Records processed files to prevent reprocessing

## Environment Variables

- **output**: Name of the output Kafka topic (default: `s3-data`)
- **S3_BUCKET**: S3 bucket URI (e.g., `s3://quix-test-bucket/configurations/`)
- **S3_REGION**: AWS region of the S3 bucket (e.g., `eu-west-2`)
- **S3_SECRET**: AWS Secret Access Key (stored as secret)
- **S3_ACCESS_KEY_ID**: AWS Access Key ID (stored as secret)
- **S3_FOLDER_PATH**: Folder path within bucket to monitor (e.g., `configurations`)
- **S3_FILE_FORMAT**: Expected file format (e.g., `xml`)
- **S3_FILE_COMPRESSION**: Compression type (e.g., `gzip`)
- **POLL_INTERVAL_SECONDS**: Polling interval in seconds (default: 30)

## Configuration Example

Based on the current deployment configuration:

```yaml
S3_BUCKET: "s3://quix-test-bucket/configurations/"
S3_REGION: "eu-west-2"
S3_FOLDER_PATH: "configurations"
S3_FILE_FORMAT: "xml"
S3_FILE_COMPRESSION: "gzip"
POLL_INTERVAL_SECONDS: "30"
```

## Data Flow

The service fits into the larger configuration management pipeline:

```
S3 Bucket → S3 Source → s3-data topic → XML-to-JSON → configurations topic → Configuration Sink → Configuration API
```

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export S3_BUCKET="s3://your-bucket/path/"
export S3_REGION="your-region"
export S3_ACCESS_KEY_ID="your-access-key"
export S3_SECRET="your-secret-key"
export S3_FOLDER_PATH="configurations"
export output="s3-data"

# Run the service
python main.py
```

### Docker Build

```bash
docker build -t s3-source .
```

## File Processing

### Supported File Types
- **XML files**: Primary configuration format
- **Gzip compression**: Automatic decompression support
- **Text-based formats**: Any text-based configuration files

### File Structure
The service expects files in the following S3 structure:
```
s3://bucket-name/configurations/
├── config1.xml.gz
├── config2.xml.gz
└── subfolder/
    └── config3.xml.gz
```

## Error Handling

- **S3 Connection Errors**: Automatic retry with exponential backoff
- **Authentication Failures**: Clear error logging for credential issues
- **File Access Errors**: Graceful handling of permission or availability issues
- **Compression Errors**: Error handling for corrupted compressed files

## State Management

The service maintains persistent state to track:
- Last processed timestamp
- File checksums/ETags to detect changes
- Processing status of individual files

State is preserved across service restarts through Quix's state management system.

## Monitoring

The service provides logging for:
- File discovery and processing events
- S3 API interactions and errors
- Kafka message publishing status
- Performance metrics and polling intervals

## Integration

This service integrates with:
- **Upstream**: S3 bucket containing configuration files
- **Downstream**: XML-to-JSON transformation service via `s3-data` topic
- **Monitoring**: Quix platform logging and metrics systems