import os
import time
import json
from quixstreams import Application
from quixstreams.sinks.core.list import ListSink


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    output_topic = os.getenv("TEST_OUTPUT_TOPIC", "test-s3-output")
    timeout = int(os.getenv("TEST_TIMEOUT", "60"))
    min_expected_messages = 3  # We expect 3 files from setup_minio.py

    print(f"Consuming from output topic: {output_topic}")
    print(f"Waiting for at least {min_expected_messages} messages with timeout of {timeout}s")

    app = Application(
        broker_address=broker_address,
        consumer_group=f"test-consumer-{int(time.time())}",
        auto_offset_reset="earliest"
    )

    topic = app.topic(output_topic)
    list_sink = ListSink()

    sdf = app.dataframe(topic)
    sdf.sink(list_sink)

    app.run(timeout=timeout, count=10)

    message_count = len(list_sink)
    print(f"Received {message_count} messages from output topic")

    if message_count < min_expected_messages:
        print(f"FAILED: Expected at least {min_expected_messages} messages, got {message_count}")
        exit(1)

    # Verify first message structure - now expects S3 metadata format
    first_message = list_sink[0]
    expected_metadata_fields = {"timestamp", "file_name", "content_type", "size",
                                  "last_modified", "url", "etag", "bucket",
                                  "original_size", "content", "part_index", "total_parts"}
    actual_fields = set(first_message.keys())

    print(f"First message keys: {actual_fields}")
    print(f"Expected metadata fields: {expected_metadata_fields}")

    if not expected_metadata_fields.issubset(actual_fields):
        missing = expected_metadata_fields - actual_fields
        print(f"FAILED: Missing fields: {missing}")
        print(f"Full message: {first_message}")
        exit(1)

    # Verify metadata field types
    if not isinstance(first_message["file_name"], str):
        print(f"FAILED: 'file_name' should be string, got {type(first_message['file_name'])}")
        exit(1)

    if not isinstance(first_message["size"], int):
        print(f"FAILED: 'size' should be integer, got {type(first_message['size'])}")
        exit(1)

    if not isinstance(first_message["bucket"], str):
        print(f"FAILED: 'bucket' should be string, got {type(first_message['bucket'])}")
        exit(1)

    if first_message["bucket"] != "test-bucket":
        print(f"FAILED: Expected bucket 'test-bucket', got {first_message['bucket']}")
        exit(1)

    print("Metadata field types validated successfully")

    # Verify that we have content (since DOWNLOAD_CONTENT=True)
    if first_message["content"] is None:
        print(f"FAILED: Expected content to be downloaded, but got None")
        exit(1)

    # Verify file names
    file_names = set(msg["file_name"] for msg in list_sink)
    print(f"File names found: {file_names}")

    # We expect files in the data/ folder
    expected_prefix = "data/"
    for file_name in file_names:
        if not file_name.startswith(expected_prefix):
            print(f"FAILED: Expected file names to start with '{expected_prefix}', got {file_name}")
            exit(1)

    print(f"SUCCESS: Verified {message_count} messages with correct S3 metadata structure and {len(file_names)} unique files")
    exit(0)


if __name__ == "__main__":
    main()
