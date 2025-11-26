from quixstreams.sinks import BatchingSink, SinkBatch
import boto3
from botocore.exceptions import ClientError
from s3transfer.manager import TransferManager, TransferConfig
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import time
import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from io import BytesIO
from catalog_client import CatalogClient


TIMESTAMP_COL_MAPPER = {
    "year": lambda col: col.dt.year.astype(str),
    "month": lambda col: col.dt.month.astype(str).str.zfill(2),
    "day": lambda col: col.dt.day.astype(str).str.zfill(2),
    "hour": lambda col: col.dt.hour.astype(str).str.zfill(2)
}

logger = logging.getLogger('quixstreams')


class QuixLakeSink(BatchingSink):
    """
    Writes Kafka batches directly to S3 as Hive-partitioned Parquet files,
    then optionally registers the table using the discover endpoint.
    """
    
    def __init__(
        self,
        s3_bucket: str,
        s3_prefix: str,
        table_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_region: str = "us-east-1",
        s3_endpoint_url: Optional[str] = None,
        hive_columns: List[str] = None,
        timestamp_column: str = "ts_ms",
        catalog_url: Optional[str] = None,
        catalog_auth_token: Optional[str] = None,
        auto_discover: bool = True,
        namespace: str = "default",
        auto_create_bucket: bool = True,
        max_workers: int = 10
    ):
        """
        Initialize S3 Direct Sink

        Args:
            s3_bucket: S3 bucket name
            s3_prefix: S3 prefix/path for data files
            table_name: Table name for registration
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            aws_region: AWS region (default: "us-east-1")
            s3_endpoint_url: Custom S3 endpoint URL for non-AWS S3-compatible storage
                           (e.g., MinIO, Wasabi, DigitalOcean Spaces)
            hive_columns: List of columns to use for Hive partitioning. Include 'year', 'month',
                         'day', 'hour' to extract these from timestamp_column
            timestamp_column: Column containing timestamp to extract time partitions from
            catalog_url: Optional REST Catalog URL for table registration
            catalog_auth_token: If using REST Catalog, the respective auth token for it
            auto_discover: Whether to auto-register table on first write
            namespace: Catalog namespace (default: "default")
            auto_create_bucket: if True, create bucket in S3 if missing.
            max_workers: Maximum number of parallel upload threads (default: 10)
        """
        self._aws_region = aws_region
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._aws_endpoint_url = s3_endpoint_url
        self._credentials = {
            "region_name": self._aws_region,
            "aws_access_key_id": self._aws_access_key_id,
            "aws_secret_access_key": self._aws_secret_access_key,
            "endpoint_url": self._aws_endpoint_url,
        }
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.table_name = table_name
        self.hive_columns = hive_columns or []
        self.timestamp_column = timestamp_column
        self._catalog = CatalogClient(catalog_url, catalog_auth_token) if catalog_url else None
        self.auto_discover = auto_discover
        self.namespace = namespace
        self.table_registered = False

        # S3 client will be initialized in setup()
        self.s3_client = None
        self._ts_hive_columns = {'year', 'month', 'day', 'hour'} & set(self.hive_columns)
        self._auto_create_bucket = auto_create_bucket
        self._max_workers = max_workers

        # Batch upload tracking with TransferManager
        self._pending_futures = []
        self._transfer_manager = None

        super().__init__()
    
    def setup(self):
        """Initialize S3 client and test connection"""
        logger.info("Starting S3 Direct Sink...")
        logger.info(f"S3 Target: s3://{self.s3_bucket}/{self.s3_prefix}/{self.table_name}")
        logger.info(f"Partitioning: hive_columns={self.hive_columns}")

        if self._aws_endpoint_url:
            logger.info(f"Using custom S3 endpoint: {self._aws_endpoint_url}")

        if self._catalog and self.auto_discover:
            logger.info(f"Table will be auto-registered in REST Catalog on first write")

        try:
            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                **self._credentials
            )

            # Initialize TransferManager for concurrent uploads
            transfer_config = TransferConfig(max_request_concurrency=self._max_workers)
            self._transfer_manager = TransferManager(self.s3_client, config=transfer_config)

            # Confirm bucket connection
            self._ensure_bucket()

            # Test Catalog connection if configured
            if self._catalog:
                try:
                    response = self._catalog.get("/health", timeout=5)
                    response.raise_for_status()
                    logger.info("Successfully connected to REST Catalog at %s", self._catalog)
                except Exception as e:
                    logger.warning("Could not connect to REST Catalog: %s. Table registration disabled.", e)
                    self.auto_discover = False

            # Check if table already exists in S3 and validate partition strategy
            self._validate_existing_table_structure()

        except Exception as e:
            logger.error("Failed to setup S3 connection: %s", e)
            raise

    def _ensure_bucket(self):
        bucket = self.s3_bucket
        try:
            self.s3_client.head_bucket(Bucket=bucket)
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404 and self._auto_create_bucket:
                # Bucket does not exist, create it
                logger.debug(f"⚠️ Bucket '{bucket}' not found. Creating it...")
                self.s3_client.create_bucket(Bucket=self.s3_bucket)
                logger.info(f"✅ Bucket '{bucket}' created.")
            else:
                raise
        logger.info("Successfully connected to S3 bucket: %s", bucket)

    def write(self, batch: SinkBatch):
        """Write batch directly to S3"""
        # Register table before first write if auto-discover is enabled
        if self.auto_discover and not self.table_registered and self._catalog:
            self._register_table()
            
        attempts = 3
        while attempts:
            start = time.perf_counter()
            try:
                self._write_batch(batch)
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.info("✔ wrote %d rows to S3 in %.1f ms", batch.size, elapsed_ms)
                return
            except Exception as exc:
                attempts -= 1
                if attempts == 0:
                    raise
                logger.warning("Write failed (%s) – retrying …", exc)
                time.sleep(3)
    
    def _write_batch(self, batch: SinkBatch):
        """Convert batch to Parquet and write to S3 with Hive partitioning"""
        if not batch:
            return

        # Convert batch to list of dictionaries
        rows = []
        for item in batch:
            row = item.value.copy()
            # Add timestamp and key if not present
            # This ensures we have a timestamp column for time-based partitioning
            if self.timestamp_column not in row:
                row[self.timestamp_column] = item.timestamp
            row["__key"] = item.key
            rows.append(row)

        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(rows)

        # Add time-based partition columns (year/month/day/hour) if they're specified in hive_columns
        # These are extracted from the timestamp_column
        if self._ts_hive_columns:
            df = self._add_timestamp_columns(df)

        # Use only the explicitly specified partition columns
        if partition_columns := self.hive_columns.copy():
            # Group by partition columns and write each partition separately
            # This creates the Hive-style directory structure: col1=val1/col2=val2/file.parquet
            for group_values, group_df in df.groupby(partition_columns):
                # Ensure group_values is always a tuple for consistent handling
                if not isinstance(group_values, tuple):
                    group_values = (group_values,)

                # Build S3 key with Hive partitioning (col=value format)
                # Example: s3://bucket/prefix/table/year=2024/month=01/day=15/data_abc123.parquet
                partition_parts = [f"{col}={val}" for col, val in zip(partition_columns, group_values)]
                s3_key = f"{self.s3_prefix}/{self.table_name}/" + "/".join(partition_parts) + f"/data_{uuid.uuid4().hex}.parquet"

                # Remove partition columns from data (Hive style - partition values are in the path, not the data)
                data_df = group_df.drop(columns=partition_columns, errors='ignore')

                # Write to S3
                self._write_parquet_to_s3(data_df, s3_key, partition_columns, group_values)
        else:
            # No partitioning - write as single file directly under table directory
            s3_key = f"{self.s3_prefix}/{self.table_name}/data_{uuid.uuid4().hex}.parquet"
            self._write_parquet_to_s3(df, s3_key, [], ())

        # Wait for all uploads to complete and register files in catalog
        self._finalize_writes()

    def _write_parquet_to_s3(
        self,
        df: pd.DataFrame,
        s3_key: str,
        partition_columns: List[str],
        partition_values: tuple
    ):
        # Convert to Arrow table and prepare buffer
        self._null_empty_dicts(df)
        table = pa.Table.from_pandas(df)

        buf = pa.BufferOutputStream()
        pq.write_table(table, buf)
        parquet_bytes = buf.getvalue().to_pybytes()

        # Submit upload to TransferManager
        future = self._transfer_manager.upload(
            BytesIO(parquet_bytes),
            self.s3_bucket,
            s3_key
        )

        self._pending_futures.append({
            'future': future,
            'key': s3_key,
            'row_count': len(df),
            'file_size': len(parquet_bytes),
            'partition_columns': partition_columns,
            'partition_values': partition_values
        })

    def _finalize_writes(self):
        """Wait for all pending uploads to complete and register files in catalog"""
        if not self._pending_futures:
            return

        count = len(self._pending_futures)
        logger.debug(f"Waiting for {count} upload(s) to complete...")

        # Wait for all uploads to complete
        for item in self._pending_futures:
            try:
                item['future'].result()  # Wait and raise on error
                logger.debug("✓ Uploaded %d rows to s3://%s/%s",
                           item['row_count'], self.s3_bucket, item['key'])
            except Exception as e:
                logger.error("✗ Failed to upload s3://%s/%s: %s",
                           self.s3_bucket, item['key'], e)
                raise

        logger.info(f"✓ Successfully uploaded {count} file(s)")

        # Register all files in catalog manifest if configured
        if self._catalog and self.table_registered:
            self._register_files_in_manifest()

        # Clear the futures list
        self._pending_futures.clear()

    def _null_empty_dicts(self, df: pd.DataFrame):
        """
        Convert empty dictionaries to null values before writing to Parquet.

        Parquet format has limitations with empty maps/structs - they cannot be written
        properly and will cause serialization errors. This method scans all columns
        that contain dictionaries and replaces empty dicts ({}) with None/null values.

        This is done in-place to avoid copying the DataFrame.
        """
        for col in df.columns:
            # Check if column contains any dictionary values
            if df[col].apply(lambda x: isinstance(x, dict)).any():
                # Replace empty dicts with None; keeps non-empty dicts as-is
                df[col] = df[col].apply(lambda x: x or None)

    def _register_table(self):
        """Register the table in REST Catalog"""
        if not self._catalog:
            return
            
        try:
            # First check if table already exists
            check_response = self._catalog.get(
                f"/namespaces/{self.namespace}/tables/{self.table_name}",
                timeout=5
            )
            
            if check_response.status_code == 200:
                logger.info("Table '%s' already exists in catalog", self.table_name)
                self.table_registered = True
                # Validate partition strategy matches
                self._validate_partition_strategy(check_response.json())
                return
            
            # Table doesn't exist, create it
            s3_path = f"s3://{self.s3_bucket}/{self.s3_prefix}/{self.table_name}"
            
            # Define partition spec based on configuration
            # For dynamic partition discovery, create table without partition spec
            # The partition spec will be set when first files are added
            partition_spec = []  # Empty spec for dynamic discovery
            
            # Create table with minimal schema (will be inferred from data)
            create_response = self._catalog.put(
                f"/namespaces/{self.namespace}/tables/{self.table_name}",
                json={
                    "location": s3_path,
                    "partition_spec": partition_spec,  # Empty for dynamic discovery
                    "properties": {
                        "created_by": "quix-lake-sink",
                        "auto_discovered": "false",
                        "expected_partitions": self.hive_columns.copy()  # Store expected partitions in properties
                    }
                },
                timeout=30
            )
            
            if create_response.status_code in [200, 201]:
                logger.info(
                    "Successfully created table '%s' in REST Catalog. Partitions will be set dynamically to: %s",
                    self.table_name,
                    self.hive_columns
                )
                self.table_registered = True
            else:
                logger.warning(
                    "Failed to create table '%s': %s", 
                    self.table_name, 
                    create_response.text
                )
                
        except Exception as e:
            logger.warning("Failed to register table '%s': %s", self.table_name, e)
    
    def _add_timestamp_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add timestamp-based columns (year/month/day/hour) for time-based partitioning.

        This method extracts time components from the timestamp column and adds them
        as separate columns that can be used for Hive partitioning.
        """
        # Convert to datetime if needed (handles numeric timestamps)
        if not pd.api.types.is_datetime64_any_dtype(df[self.timestamp_column]):
            sample_value = float(df[self.timestamp_column].iloc[0] if not df[self.timestamp_column].empty else 0)

            # Auto-detect timestamp unit by inspecting the magnitude of the value
            # Typical timestamp ranges:
            # - Seconds: ~1.7e9 (since epoch 1970)
            # - Milliseconds: ~1.7e12
            # - Microseconds: ~1.7e15
            # - Nanoseconds: ~1.7e18
            if sample_value > 1e17:
                # Nanoseconds (Java/Kafka timestamps)
                df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column], unit='ns')
            elif sample_value > 1e14:
                # Microseconds
                df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column], unit='us')
            elif sample_value > 1e11:
                # Milliseconds (common in JavaScript/Kafka)
                df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column], unit='ms')
            else:
                # Seconds (Unix timestamp)
                df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column], unit='s')

        # Extract time-based columns (year, month, day, hour) from the timestamp
        timestamp_col = df[self.timestamp_column]

        # Only add columns that are specified in _ts_hive_columns
        # TIMESTAMP_COL_MAPPER handles proper formatting (e.g., zero-padding for months/days)
        for col in self._ts_hive_columns:
            df[col] = TIMESTAMP_COL_MAPPER[col](timestamp_col)

        return df
    
    def _validate_partition_strategy(self, table_metadata: Dict[str, Any]):
        """Validate that the sink's partition strategy matches the existing table"""
        existing_partition_spec = table_metadata.get("partition_spec", [])
        
        # Build expected partition spec from sink configuration
        expected_partition_spec = self.hive_columns.copy()
        
        # Special case: If table has no partition spec yet (empty list), 
        # it will be set when first files are added
        if not existing_partition_spec:
            logger.info(
                "Table '%s' has no partition spec yet. Will be set to %s on first write.",
                self.table_name,
                expected_partition_spec
            )
            return
        
        # Check if partition strategies match
        if set(existing_partition_spec) != set(expected_partition_spec):
            error_msg = (
                f"Partition strategy mismatch for table '{self.table_name}'. "
                f"Existing table has partitions: {existing_partition_spec}, "
                f"but sink is configured with: {expected_partition_spec}. "
                "This would corrupt the folder structure. Please ensure the sink partition "
                "configuration matches the existing table."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Also check the order of partitions
        if existing_partition_spec != expected_partition_spec:
            warning_msg = (
                f"Partition column order differs for table '{self.table_name}'. "
                f"Existing: {existing_partition_spec}, Configured: {expected_partition_spec}. "
                "While this won't corrupt data, it may lead to suboptimal query performance."
            )
            logger.warning(warning_msg)
    
    def _validate_existing_table_structure(self):
        """
        Check if table already exists in S3 and validate partition structure.

        This prevents data corruption by ensuring that if a table already exists in S3,
        the sink's partition configuration matches what's already on disk. Mismatched
        partition strategies would result in a corrupted folder structure that would
        make the data unqueryable.
        """
        table_prefix = f"{self.s3_prefix}/{self.table_name}/"

        try:
            # List objects to see if table exists (sample first 100 files)
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=table_prefix,
                MaxKeys=100
            )

            if 'Contents' not in response:
                # Table doesn't exist yet, no validation needed
                return

            # Detect existing partition columns from S3 directory structure
            # We parse the S3 paths to extract partition columns from Hive-style paths
            detected_partition_columns = []
            for obj in response['Contents']:
                if obj['Key'].endswith('.parquet'):
                    # Extract path after table prefix
                    # Example: "year=2024/month=01/day=15/data.parquet" -> ["year=2024", "month=01", "day=15", "data.parquet"]
                    relative_path = obj['Key'][len(table_prefix):]
                    path_parts = relative_path.split('/')

                    # Look for Hive-style partitions (col=value format)
                    for part in path_parts[:-1]:  # Exclude filename
                        if '=' in part:
                            # Extract column name from "col=value"
                            col_name = part.split('=')[0]
                            # Maintain order of first appearance
                            if col_name not in detected_partition_columns:
                                detected_partition_columns.append(col_name)

            if detected_partition_columns:
                # Build expected partition spec from sink configuration
                expected_partition_spec = self.hive_columns.copy()

                # Check if partition strategies match
                # Using set comparison to ignore order first
                if set(detected_partition_columns) != set(expected_partition_spec):
                    error_msg = (
                        f"Partition strategy mismatch for table '{self.table_name}'. "
                        f"Existing table in S3 has partitions: {detected_partition_columns}, "
                        f"but sink is configured with: {expected_partition_spec}. "
                        "This would corrupt the folder structure. Please ensure the sink partition "
                        "configuration matches the existing table."
                    )
                    logger.error(error_msg)
                    raise ValueError(error_msg)

                logger.info(
                    "Validated partition strategy for existing table '%s'. Partitions: %s",
                    self.table_name,
                    detected_partition_columns
                )

        except self.s3_client.exceptions.NoSuchBucket:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.warning(
                "Could not validate existing table structure: %s. Proceeding with caution.", e
            )
    
    def _register_files_in_manifest(self):
        """Register multiple newly written files in the catalog manifest"""
        if not (file_items := self._pending_futures):
            return

        try:
            # Build file entries for all files
            file_entries = []
            for item in file_items:
                s3_key = item['key']
                row_count = item['row_count']
                file_size = item['file_size']
                partition_columns = item['partition_columns']
                partition_values = item['partition_values']

                # Build S3 URL
                file_path = f"s3://{self.s3_bucket}/{s3_key}"

                # Build partition values dict
                partition_dict = {}
                if partition_columns and partition_values:
                    for col, val in zip(partition_columns, partition_values):
                        partition_dict[col] = str(val)

                # Create file entry
                file_entries.append({
                    "file_path": file_path,
                    "file_size": file_size,
                    "last_modified": datetime.now(tz=timezone.utc).isoformat(),
                    "partition_values": partition_dict,
                    "row_count": row_count
                })

            # Send all files to catalog in a single request
            response = self._catalog.post(
                f"/namespaces/{self.namespace}/tables/{self.table_name}/manifest/add-files",
                json={"files": file_entries},
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"✓ Registered {len(file_entries)} file(s) in catalog manifest")
            else:
                logger.warning("Failed to register files in manifest: %s", response.text)

        except Exception as e:
            # Don't fail the write if manifest registration fails
            logger.warning("Failed to register files in manifest: %s", e)