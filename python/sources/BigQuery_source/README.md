# BigQuery to Kafka Connector

A Python utility that extracts data from Google BigQuery and publishes it to a Kafka topic using Quix Streams.

## Overview

This connector reads data from a BigQuery table and streams it to a Kafka topic, handling various data types and serialization challenges. It's built with Quix Streams for Kafka integration and includes custom serialization to properly handle all BigQuery data types.

## Features

- Connects to BigQuery using service account authentication
- Extracts data using custom SQL queries
- Handles complex data types including:
  - Datetime objects
  - Decimal values
  - Binary data
  - NULL/NA values
  - Time objects
- Publishes data to Kafka topics with proper serialization
- Error handling for serialization issues

## Prerequisites

- Python 3.7+
- Access to a Google Cloud project with BigQuery
- A Kafka cluster configured with Quix
- Service account credentials with BigQuery access

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install quixstreams google-cloud-bigquery pandas python-dotenv
```

## Configuration

The script uses environment variables for configuration:

- `output`: Kafka topic name to publish data to
- `service_account`: JSON string containing the Google Cloud service account credentials

For local development, you can use a `.env` file with these variables.

## Usage

1. Set the environment variables or create a `.env` file
2. Modify the SQL query in the `read_data()` function to match your BigQuery table
3. Run the script:

```bash
python bigquery_to_kafka.py
```

## How It Works

1. The script establishes a connection to BigQuery using the provided service account credentials
2. It executes the SQL query to fetch data from the specified table
3. Each row is converted to a JSON-serializable format with custom handling for special data types
4. The data is serialized and published to the Kafka topic
5. Error handling captures and logs any serialization issues without stopping the entire process

## Custom Data Type Handling

The script includes two custom classes for data serialization:

- `CustomJSONEncoder`: Extends the standard JSON encoder to handle BigQuery-specific data types
- `BigQuerySerializer`: Handles pre-processing of data before serialization

## Error Handling

The script includes comprehensive error handling that:
- Catches exceptions during serialization
- Logs problematic data with detailed information
- Continues processing other rows when errors occur

## Contributing

Feel free to submit issues or pull requests for improvements to the connector.

## License

This project is open source under the Apache 2.0 license.
