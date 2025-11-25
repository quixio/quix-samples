import logging
import time
import json
import os
import math
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from quixstreams.models.topics import Topic
from quixstreams.sources.base import StatefulSource

logger = logging.getLogger(__name__)


class S3FileWatcher(StatefulSource):
    def __init__(
        self,
        name: str,
        bucket_name: str,
        folder_prefix: str = "",
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        region_name: str = 'us-east-1',
        endpoint_url: str = None,
        poll_interval: int = 30
    ) -> None:
        # Clean bucket name - remove s3:// prefix if present
        if bucket_name.startswith('s3://'):
            parts = bucket_name[5:].split('/', 1)
            bucket_name = parts[0]
            if len(parts) > 1 and not folder_prefix:
                folder_prefix = parts[1]

        bucket_name = bucket_name.rstrip('/')
        if folder_prefix and not folder_prefix.endswith('/'):
            folder_prefix += '/'

        self.bucket_name = bucket_name
        self.folder_prefix = folder_prefix
        self.poll_interval = poll_interval
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.endpoint_url = endpoint_url

        # Read DOWNLOAD_CONTENT from environment (optional)
        download_content_env = os.getenv("DOWNLOAD_CONTENT", "True")
        self.download_content = download_content_env.lower() in ("true", "1", "yes")

        # Read MAX_MB_PER_MESSAGE from environment (optional)
        max_mb_env = os.getenv("MAX_MB_PER_MESSAGE")

        try:
            if max_mb_env is not None:
                self.max_mb_per_message = float(max_mb_env)
            else:
                self.max_mb_per_message = 1.0  # default MB limit
        except ValueError:
            logger.warning("Invalid MAX_MB_PER_MESSAGE value, falling back to 1 MB.")
            self.max_mb_per_message = 1.0

        # Enforce positive value
        if self.max_mb_per_message <= 0:
            logger.warning("MAX_MB_PER_MESSAGE <= 0, chunking disabled.")
            self.max_mb_per_message = None
            self.max_bytes_per_message = None
        else:
            # Convert MB → bytes (integer!)
            self.max_bytes_per_message = int(self.max_mb_per_message * 1024 * 1024)
            logger.info(
                f"MAX_MB_PER_MESSAGE set: {self.max_mb_per_message} MB -> {self.max_bytes_per_message} bytes"
            )

        # Debug logging
        logger.info(f"S3FileWatcher initialized:")
        logger.info(f"  Bucket: '{self.bucket_name}'")
        logger.info(f"  Folder prefix: '{self.folder_prefix}'")
        logger.info(f"  Region: '{self.region_name}'")
        logger.info(f"  Poll interval: {self.poll_interval}s")
        logger.info(f"  Download content: {self.download_content}")
        if self.max_bytes_per_message:
            logger.info(f"  Max message size (bytes): {self.max_bytes_per_message}")

        super().__init__(name=name, shutdown_timeout=10)

    def setup(self):
        client_kwargs = {'region_name': self.region_name}

        if self.aws_access_key_id and self.aws_secret_access_key:
            client_kwargs['aws_access_key_id'] = self.aws_access_key_id
            client_kwargs['aws_secret_access_key'] = self.aws_secret_access_key

        if self.endpoint_url:
            client_kwargs['endpoint_url'] = self.endpoint_url

        self.s3_client = boto3.client('s3', **client_kwargs)

        self.last_check = datetime.min

    def _get_new_files(self):
        """Get list of new files since last check"""
        try:
            list_params = {'Bucket': self.bucket_name}
            if self.folder_prefix:
                list_params['Prefix'] = self.folder_prefix
                logger.debug(f"Listing objects with prefix: {self.folder_prefix}")

            response = self.s3_client.list_objects_v2(**list_params)

            new_files = []
            current_time = datetime.now()

            if 'Contents' in response:
                logger.info(f"Found {len(response['Contents'])} total objects in bucket")
                for obj in response['Contents']:
                    if obj['Key'].endswith('/'):
                        continue

                    if (obj['Key'] not in self.processed_files and
                            obj['LastModified'].replace(tzinfo=None) > self.last_check):
                        new_files.append(obj)
                        logger.debug(f"New file found: {obj['Key']}")
                    else:
                        logger.debug(f"File {obj['Key']} already processed or not new.")
            else:
                logger.info("No objects found in bucket/folder")

            self.last_check = current_time
            return new_files

        except ClientError as e:
            logger.error(f"Error listing S3 objects: {e}")
            return []
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing S3 objects: {e}")
            return []

    def _download_file_content(self, file_key):
        """Download file content and metadata"""
        try:
            head_response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            # Generate appropriate URL based on endpoint
            if self.endpoint_url:
                s3_url = f"{self.endpoint_url}/{self.bucket_name}/{file_key}"
            else:
                s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"

            file_data = {
                "file_name": file_key,
                "content_type": head_response.get('ContentType', 'application/octet-stream'),
                "size": head_response.get('ContentLength', 0),
                "last_modified": head_response.get('LastModified', datetime.now()).isoformat(),
                "url": s3_url,
                "etag": head_response.get('ETag', '').strip('"')
            }

            # Only download content if DOWNLOAD_CONTENT is True
            if self.download_content:
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
                file_data["content"] = response['Body'].read()
            else:
                file_data["content"] = None

            return file_data

        except ClientError as e:
            logger.error(f"Error downloading file {file_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading file {file_key}: {e}")
            return None

    def _produce_message_chunked(self, file_key: str, file_data: dict) -> bool:
        """Produce the file content either in a single message or in multiple chunks."""
        try:
            content_bytes = file_data["content"] or b""
            original_size = len(content_bytes)

            base_message = {
                "timestamp": datetime.now().isoformat(),
                "file_name": file_data["file_name"],
                "content_type": file_data["content_type"],
                "size": file_data["size"],
                "last_modified": file_data["last_modified"],
                "url": file_data["url"],
                "etag": file_data["etag"],
                "bucket": self.bucket_name,
                "original_size": original_size
            }

            # If content is not downloaded, send metadata only
            if not self.download_content:
                base_message["content"] = None
                base_message["part_index"] = 1
                base_message["total_parts"] = 1

                self.produce(
                    key=file_key,
                    value=json.dumps(base_message).encode('utf-8')
                )
                logger.info(f"Published metadata-only message for {file_key}")
                return True

            # If no max size set, or content fits in one message -> send as single message
            if not self.max_bytes_per_message or original_size <= self.max_bytes_per_message:
                base_message["content"] = content_bytes.decode('utf-8', errors='ignore') if content_bytes else ""
                base_message["part_index"] = 1
                base_message["total_parts"] = 1

                self.produce(
                    key=file_key,
                    value=json.dumps(base_message).encode('utf-8')
                )
                logger.info(f"Published single-part file {file_key} ({original_size} bytes)")
                return True

            # Otherwise chunk it
            total_parts = math.ceil(original_size / self.max_bytes_per_message)
            logger.info(
                f"File {file_key} is {original_size} bytes, splitting into {total_parts} parts "
                f"of up to {self.max_bytes_per_message} bytes"
            )

            for part_index in range(total_parts):
                start = part_index * self.max_bytes_per_message
                end = min(start + self.max_bytes_per_message, original_size)
                chunk = content_bytes[start:end]

                message = base_message.copy()
                message["content"] = chunk.decode('utf-8', errors='ignore') if chunk else ""
                message["part_index"] = part_index + 1
                message["total_parts"] = total_parts
                message["chunk_size"] = len(chunk)
                message["chunk_start"] = start
                message["chunk_end"] = end

                self.produce(
                    key=f"{file_key}.part{part_index+1:04d}",
                    value=json.dumps(message).encode('utf-8')
                )
                logger.debug(f"Published chunk {part_index+1}/{total_parts} for {file_key} ({len(chunk)} bytes)")

            logger.info(f"Published all {total_parts} parts for {file_key}")
            return True

        except Exception as e:
            logger.error(f"Error producing message(s) for {file_key}: {e}")
            return False

    def run(self):
        """Main run method for the source"""
        logger.info("Starting S3 File Watcher...")
        logger.info(f"Monitoring bucket: {self.bucket_name}")
        logger.info(f"Poll interval: {self.poll_interval} seconds")

        self.processed_files = set(self.state.get("processed_files", []))
        logger.info(f"Loaded {len(self.processed_files)} previously processed files")

        try:
            while self.running:
                new_files = self._get_new_files()

                if new_files:
                    logger.info(f"Found {len(new_files)} new file(s)")
                    for file_obj in new_files:
                        if not self.running:
                            break

                        file_key = file_obj['Key']
                        logger.info(f"Processing file: {file_key}")

                        file_data = self._download_file_content(file_key)
                        if file_data:
                            success = self._produce_message_chunked(file_key, file_data)

                            if success:
                                self.processed_files.add(file_key)
                                self.state.set("processed_files", list(self.processed_files))
                                self.flush()
                                logger.info(f"Published file {file_key} to topic and marked as processed")
                            else:
                                logger.error(f"Failed to publish file (or its chunks): {file_key}")
                        else:
                            logger.error(f"Failed to download file: {file_key}")

                time.sleep(self.poll_interval)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            raise
        finally:
            self.flush()
            logger.info("S3 File Watcher stopped")

    def default_topic(self) -> Topic:
        """Default topic configuration"""
        return Topic(
            name=self.name,
            key_serializer="string",
            key_deserializer="string",
            value_deserializer="json",
            value_serializer="json",
        )