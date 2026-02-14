"""
FMU Runner - Processes FMU simulation requests from Kafka

Consumes from 'simulation' topic, filters for .fmu files,
executes FMU simulation using fmpy, outputs to 'simulation-results' topic.

This is a lightweight runner that doesn't require MATLAB Runtime - it 
processes FMU (Functional Mock-up Unit) files instead.
"""
import os
import logging
from datetime import datetime, timezone

import boto3
from botocore.client import Config
from quixstreams import Application
from dotenv import load_dotenv

from fmu_executor import should_process, run_fmu_simulation

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOGLEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# S3 Configuration
S3_ENDPOINT = os.environ.get("S3_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "minioadmin")
S3_BUCKET = os.environ.get("S3_BUCKET", "fmu-models")
STATE_DIR = os.getenv("state_dir", "state")

# Initialize S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=Config(signature_version='s3v4')
)

# Ensure state directory exists
os.makedirs(os.path.join(STATE_DIR, "fmu_cache"), exist_ok=True)


def fetch_model_from_s3(s3_path: str) -> bytes:
    """
    Fetch FMU model binary from S3.

    Args:
        s3_path: S3 object key (e.g., 'models/abc123_BouncingBall.fmu')

    Returns:
        Binary content of the FMU file

    Raises:
        RuntimeError: If fetch fails
    """
    logger.info(f"Fetching FMU from S3: {s3_path}")

    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_path)
        fmu_bytes = response['Body'].read()
        logger.info(f"Fetched FMU: {len(fmu_bytes)} bytes")
        return fmu_bytes
    except Exception as e:
        raise RuntimeError(f"Failed to fetch FMU from S3: {e}")


def get_fmu_path(model_filename: str, model_s3_path: str) -> str:
    """
    Get path to FMU file, downloading from S3 if needed.

    Args:
        model_filename: Name of the FMU file (for cache filename)
        model_s3_path: S3 object key to fetch the FMU from

    Returns:
        Path to the FMU file on disk
    """
    # Cache directory for FMU files
    cache_dir = os.path.join(STATE_DIR, "fmu_cache")

    # Use the S3 path as cache key (it includes hash already)
    # Extract just the filename part from s3 path for local cache
    cache_filename = os.path.basename(model_s3_path)
    fmu_path = os.path.join(cache_dir, cache_filename)

    # Check if already cached
    if os.path.exists(fmu_path):
        logger.debug(f"Using cached FMU: {fmu_path}")
        return fmu_path

    # Fetch from S3
    fmu_bytes = fetch_model_from_s3(model_s3_path)

    # Save to cache
    with open(fmu_path, 'wb') as f:
        f.write(fmu_bytes)
    logger.info(f"Cached FMU at: {fmu_path}")

    return fmu_path


def process_message(row: dict) -> dict:
    """
    Process a simulation request message.

    Args:
        row: Kafka message payload

    Returns:
        Result payload with simulation results, or None if not an FMU
    """
    message_key = row.get("message_key", "unknown")
    model_filename = row.get("model_filename", "")

    # Check if this is an FMU file
    if not should_process(model_filename):
        logger.debug(f"Skipping non-FMU file: {model_filename}")
        return None

    logger.info(f"Processing FMU simulation: {message_key}")
    logger.info(f"  Model: {model_filename}")

    started_at = datetime.now(timezone.utc)

    try:
        # Get FMU file path from S3
        model_s3_path = row.get("model_s3_path")
        if not model_s3_path:
            raise RuntimeError(f"No model_s3_path provided for: {model_filename}")

        fmu_path = get_fmu_path(model_filename, model_s3_path)

        # Extract simulation config
        config = row.get("config", {})
        input_data = row.get("input_data", [])

        # Add start/stop time from config if not present
        if "start_time" not in config:
            config["start_time"] = 0.0
        if "stop_time" not in config:
            config["stop_time"] = 10.0

        # Run simulation
        result = run_fmu_simulation(
            fmu_path=fmu_path,
            input_data=input_data,
            config=config
        )

        completed_at = datetime.now(timezone.utc)
        processing_time_ms = (completed_at - started_at).total_seconds() * 1000

        # Build output payload - config contains success_criteria for validation
        output = {
            "message_key": message_key,
            "submitted_at": row.get("submitted_at", started_at.isoformat().replace("+00:00", "Z")),
            "started_at": started_at.isoformat().replace("+00:00", "Z"),
            "completed_at": completed_at.isoformat().replace("+00:00", "Z"),
            "processing_time_ms": processing_time_ms,
            "model_filename": model_filename,
            "model_s3_path": model_s3_path,  # Pass through for downstream services
            "config": config,
            "source": row.get("source", "user"),
            "status": result["status"],
            "error_message": result.get("error_message"),
            "input_data": result["input_data"],
        }

        logger.info(f"Completed FMU simulation: {message_key}")
        logger.info(f"  Status: {result['status']}")
        logger.info(f"  Processing time: {processing_time_ms:.1f}ms")
        logger.info(f"  Output rows: {len(result['input_data'])}")

        return output

    except Exception as e:
        logger.error(f"FMU simulation failed: {e}")
        completed_at = datetime.now(timezone.utc)
        processing_time_ms = (completed_at - started_at).total_seconds() * 1000

        return {
            "message_key": message_key,
            "submitted_at": row.get("submitted_at", started_at.isoformat().replace("+00:00", "Z")),
            "started_at": started_at.isoformat().replace("+00:00", "Z"),
            "completed_at": completed_at.isoformat().replace("+00:00", "Z"),
            "processing_time_ms": processing_time_ms,
            "model_filename": model_filename,
            "model_s3_path": row.get("model_s3_path"),  # Pass through for downstream services
            "config": row.get("config", {}),
            "source": row.get("source", "user"),
            "status": "error",
            "error_message": str(e),
            "input_data": [],
        }


def main():
    """Main entry point for the FMU Runner service."""
    logger.info("=" * 60)
    logger.info("FMU Runner Service Starting")
    logger.info(f"  S3 Endpoint: {S3_ENDPOINT}")
    logger.info(f"  S3 Bucket: {S3_BUCKET}")
    logger.info(f"  State dir: {STATE_DIR}")
    logger.info("=" * 60)

    # Setup Quix Streams application
    app = Application(
        consumer_group=os.getenv("CONSUMER_GROUP", "fmu-runner"),
        auto_create_topics=True,
        auto_offset_reset=os.getenv("AUTO_OFFSET_RESET", "earliest")
    )

    # Get topic names from environment
    input_topic_name = os.environ.get("input", "simulation")
    output_topic_name = os.environ.get("output", "simulation-results")

    logger.info(f"Input topic: {input_topic_name}")
    logger.info(f"Output topic: {output_topic_name}")

    input_topic = app.topic(name=input_topic_name)
    output_topic = app.topic(name=output_topic_name)

    # Create streaming dataframe
    sdf = app.dataframe(topic=input_topic)

    # Filter to only process FMU files
    sdf = sdf.filter(lambda row: should_process(row.get("model_filename", "")))

    # Process each message
    sdf = sdf.apply(process_message)

    # Filter out None results (shouldn't happen after filter, but be safe)
    sdf = sdf.filter(lambda row: row is not None)

    # Write to output topic
    sdf.to_topic(output_topic)

    # Run the application
    logger.info("Starting Kafka consumer...")
    app.run()


if __name__ == "__main__":
    main()
