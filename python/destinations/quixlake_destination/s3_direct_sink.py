from quixstreams.sinks import BatchingSink, SinkBatch
import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import time
import logging
import uuid
import os
from typing import List, Dict, Any
from datetime import datetime
import requests


class S3DirectSink(BatchingSink):
    """
    Writes Kafka batches directly to S3 as Hive-partitioned Parquet files,
    then optionally registers the table using the discover endpoint.
    """
    
    def __init__(self, 
                 s3_bucket: str,
                 s3_prefix: str,
                 table_name: str,
                 hive_columns: List[str] = None,
                 timestamp_column: str = "ts_ms",
                 timestamp_format: str = "day",
                 catalog_url: str = None,
                 auto_discover: bool = True,
                 namespace: str = "default"):
        """
        Initialize S3 Direct Sink
        
        Args:
            s3_bucket: S3 bucket name
            s3_prefix: S3 prefix/path for data files
            table_name: Table name for registration
            hive_columns: List of columns to use for Hive partitioning
            timestamp_column: Column containing timestamp (for time-based partitioning)
            timestamp_format: Time partition format ('day', 'hour', 'month')
            catalog_url: Optional REST Catalog URL for table registration
            auto_discover: Whether to auto-register table on first write
            namespace: Catalog namespace (default: "default")
        """
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.table_name = table_name
        self.hive_columns = hive_columns or []
        self.timestamp_column = timestamp_column
        self.timestamp_format = timestamp_format
        self.catalog_url = catalog_url.rstrip('/') if catalog_url else None
        self.auto_discover = auto_discover
        self.namespace = namespace
        self.table_registered = False
        
        self.logger = logging.getLogger(__name__)
        
        # S3 client will be initialized in setup()
        self.s3_client = None
        
        super().__init__()
    
    def setup(self):
        """Initialize S3 client and test connection"""
        try:
            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # Test S3 access
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            self.logger.info("Successfully connected to S3 bucket: %s", self.s3_bucket)
            
            # Test Catalog connection if configured
            if self.catalog_url:
                try:
                    response = requests.get(f"{self.catalog_url}/health", timeout=5)
                    response.raise_for_status()
                    self.logger.info("Successfully connected to REST Catalog at %s", self.catalog_url)
                except Exception as e:
                    self.logger.warning("Could not connect to REST Catalog: %s. Table registration disabled.", e)
                    self.auto_discover = False
                    
        except Exception as e:
            self.logger.error("Failed to setup S3 connection: %s", e)
            raise
    
    def write(self, batch: SinkBatch):
        """Write batch directly to S3"""
        # Register table before first write if auto-discover is enabled
        if self.auto_discover and not self.table_registered and self.catalog_url:
            self._register_table()
            
        attempts = 3
        while attempts:
            start = time.perf_counter()
            try:
                self._write_batch(batch)
                elapsed_ms = (time.perf_counter() - start) * 1000
                self.logger.info("✔ wrote %d rows to S3 in %.1f ms", batch.size, elapsed_ms)
                return
            except Exception as exc:
                attempts -= 1
                if attempts == 0:
                    raise
                self.logger.warning("Write failed (%s) – retrying …", exc)
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
            if self.timestamp_column not in row:
                row[self.timestamp_column] = item.timestamp
            row["__key"] = item.key
            rows.append(row)
        
        # Convert to DataFrame
        df = pd.DataFrame(rows)
        
        # Add time-based partition columns if needed
        if self.timestamp_column in df.columns:
            df = self._add_timestamp_partitions(df)
        
        # Determine actual partition columns (hive_columns + time columns)
        partition_columns = self.hive_columns.copy()
        
        # Add time partition columns if they were generated
        time_columns = self._get_time_partition_columns()
        for col in time_columns:
            if col in df.columns and col not in partition_columns:
                partition_columns.append(col)
        
        if partition_columns:
            # Group by partition columns and write each partition
            for group_values, group_df in df.groupby(partition_columns):
                if not isinstance(group_values, tuple):
                    group_values = (group_values,)
                
                # Build S3 key with Hive partitioning
                partition_parts = [f"{col}={val}" for col, val in zip(partition_columns, group_values)]
                s3_key = f"{self.s3_prefix}/{self.table_name}/" + "/".join(partition_parts) + f"/data_{uuid.uuid4().hex}.parquet"
                
                # Remove partition columns from data (Hive style)
                data_df = group_df.drop(columns=partition_columns, errors='ignore')
                
                # Write to S3
                self._write_parquet_to_s3(data_df, s3_key)
                
                # Register file in manifest if catalog is configured
                if self.catalog_url and self.table_registered:
                    self._register_file_in_manifest(s3_key, len(data_df), partition_columns, group_values)
        else:
            # No partitioning - write as single file
            s3_key = f"{self.s3_prefix}/{self.table_name}/data_{uuid.uuid4().hex}.parquet"
            self._write_parquet_to_s3(df, s3_key)
            
            # Register file in manifest if catalog is configured
            if self.catalog_url and self.table_registered:
                self._register_file_in_manifest(s3_key, len(df), [], [])
    
    def _add_timestamp_partitions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add timestamp-based partition columns"""
        if self.timestamp_column not in df.columns:
            return df
            
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df[self.timestamp_column]):
            # Assume milliseconds if numeric
            sample_value = float(df[self.timestamp_column].iloc[0] if not df[self.timestamp_column].empty else 0)
            
            if sample_value > 1e12:  # Milliseconds
                df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column], unit='ms')
            elif sample_value > 1e9:   # Seconds  
                df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column], unit='s')
            else:
                df[self.timestamp_column] = pd.to_datetime(df[self.timestamp_column])
        
        # Add partition columns based on format
        timestamp_col = df[self.timestamp_column]
        
        if self.timestamp_format in ['day', 'hour']:
            df['year'] = timestamp_col.dt.year.astype(str)
            df['month'] = timestamp_col.dt.month.astype(str).str.zfill(2)
            df['day'] = timestamp_col.dt.day.astype(str).str.zfill(2)
            
        if self.timestamp_format == 'hour':
            df['hour'] = timestamp_col.dt.hour.astype(str).str.zfill(2)
            
        elif self.timestamp_format == 'month':
            df['year'] = timestamp_col.dt.year.astype(str)
            df['month'] = timestamp_col.dt.month.astype(str).str.zfill(2)
            
        return df
    
    def _get_time_partition_columns(self) -> List[str]:
        """Get list of time partition column names based on format"""
        if self.timestamp_format == 'day':
            return ['year', 'month', 'day']
        elif self.timestamp_format == 'hour':
            return ['year', 'month', 'day', 'hour']
        elif self.timestamp_format == 'month':
            return ['year', 'month']
        return []
    
    def _write_parquet_to_s3(self, df: pd.DataFrame, s3_key: str):
        """Write DataFrame to S3 as Parquet"""
        # Convert to Arrow table
        table = pa.Table.from_pandas(df)
        
        # Write to buffer
        buf = pa.BufferOutputStream()
        pq.write_table(table, buf)
        
        # Upload to S3
        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=s3_key,
            Body=buf.getvalue().to_pybytes()
        )
        
        self.logger.debug("Wrote %d rows to s3://%s/%s", len(df), self.s3_bucket, s3_key)
    
    def _register_table(self):
        """Register the table in REST Catalog"""
        if not self.catalog_url:
            return
            
        try:
            # First check if table already exists
            check_response = requests.get(
                f"{self.catalog_url}/namespaces/{self.namespace}/tables/{self.table_name}",
                timeout=5
            )
            
            if check_response.status_code == 200:
                self.logger.info("Table '%s' already exists in catalog", self.table_name)
                self.table_registered = True
                return
            
            # Table doesn't exist, create it
            s3_path = f"s3://{self.s3_bucket}/{self.s3_prefix}/{self.table_name}"
            
            # Define partition spec based on configuration
            partition_spec = self.hive_columns.copy()
            
            # Add time partition columns
            time_columns = self._get_time_partition_columns()
            for col in time_columns:
                if col not in partition_spec:
                    partition_spec.append(col)
            
            # Create table with minimal schema (will be inferred from data)
            create_response = requests.put(
                f"{self.catalog_url}/namespaces/{self.namespace}/tables/{self.table_name}",
                json={
                    "location": s3_path,
                    "partition_spec": partition_spec,
                    "properties": {
                        "created_by": "quix-lake-sink",
                        "auto_discovered": "false"
                    }
                },
                timeout=30
            )
            
            if create_response.status_code in [200, 201]:
                self.logger.info(
                    "Successfully created table '%s' in REST Catalog with partitions: %s",
                    self.table_name,
                    partition_spec
                )
                self.table_registered = True
            else:
                self.logger.warning(
                    "Failed to create table '%s': %s", 
                    self.table_name, 
                    create_response.text
                )
                
        except Exception as e:
            self.logger.warning("Failed to register table '%s': %s", self.table_name, e)
    
    def _register_file_in_manifest(self, s3_key: str, row_count: int, 
                                  partition_columns: List[str], partition_values: tuple):
        """Register a newly written file in the catalog manifest"""
        try:
            # Build S3 URL
            file_path = f"s3://{self.s3_bucket}/{s3_key}"
            
            # Get file size
            try:
                response = self.s3_client.head_object(Bucket=self.s3_bucket, Key=s3_key)
                file_size = response['ContentLength']
            except:
                file_size = 0
            
            # Build partition values dict
            partition_dict = {}
            if partition_columns and partition_values:
                for col, val in zip(partition_columns, partition_values):
                    partition_dict[col] = str(val)
            
            # Create file entry
            file_entry = {
                "file_path": file_path,
                "file_size": file_size,
                "last_modified": datetime.utcnow().isoformat(),
                "partition_values": partition_dict,
                "row_count": row_count
            }
            
            # Send to catalog
            response = requests.post(
                f"{self.catalog_url}/namespaces/{self.namespace}/tables/{self.table_name}/manifest/add-files",
                json={"files": [file_entry]},
                timeout=5
            )
            
            if response.status_code == 200:
                self.logger.debug("Registered file in manifest: %s", file_path)
            else:
                self.logger.warning("Failed to register file in manifest: %s", response.text)
                
        except Exception as e:
            # Don't fail the write if manifest registration fails
            self.logger.warning("Failed to register file in manifest: %s", e)