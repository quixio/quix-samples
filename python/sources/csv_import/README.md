# CSV Import

Upload CSV files via a web UI and stream each row as a message to a Kafka topic in real time. Rows are streamed as they upload — no need to wait for the full file.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup) account or log in and visit the Samples to use this project.

Click **Deploy** to launch a pre-built container, or **Edit code** to fork and customize.

## Environment variables

- **output**: Kafka topic to send CSV rows to (default: `csv-data`)
- **batch_size**: Number of rows per batch (default: `1000`)

## How it works

1. Open the web UI and drag & drop a CSV file
2. Click **Send to Kafka**
3. Each row is parsed and sent as a JSON message with the filename (without extension) as the Kafka key

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.
