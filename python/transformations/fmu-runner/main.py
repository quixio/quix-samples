"""
FMU Runner - Processes FMU simulation requests from Kafka

Consumes from 'simulation' topic, filters for .fmu files,
executes FMU simulation using fmpy, outputs to 'simulation-results' topic.
"""
import os
import logging
from datetime import datetime, timezone

from quixstreams import Application
from dotenv import load_dotenv

from fmu_executor import should_process, run_fmu_simulation

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOGLEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FMU path - configurable via environment variable
FMU_PATH = os.getenv("FMU_PATH", os.path.join(os.path.dirname(__file__), "tests/fixtures/BouncingBall.fmu"))


def get_fmu_path() -> str:
    """Return the configured FMU file path."""
    return FMU_PATH


def process_message(row: dict) -> dict:
    """Process a simulation request message."""
    message_key = row.get("message_key", "unknown")
    model_filename = row.get("model_filename", "")

    if not should_process(model_filename):
        logger.debug(f"Skipping non-FMU file: {model_filename}")
        return None

    logger.info(f"Processing FMU simulation: {message_key}")
    started_at = datetime.now(timezone.utc)

    try:
        fmu_path = get_fmu_path()
        config = row.get("config", {})
        input_data = row.get("input_data", [])

        if "start_time" not in config:
            config["start_time"] = 0.0
        if "stop_time" not in config:
            config["stop_time"] = 10.0

        result = run_fmu_simulation(
            fmu_path=fmu_path,
            input_data=input_data,
            config=config
        )

        completed_at = datetime.now(timezone.utc)
        processing_time_ms = (completed_at - started_at).total_seconds() * 1000

        output = {
            "message_key": message_key,
            "submitted_at": row.get("submitted_at", started_at.isoformat().replace("+00:00", "Z")),
            "started_at": started_at.isoformat().replace("+00:00", "Z"),
            "completed_at": completed_at.isoformat().replace("+00:00", "Z"),
            "processing_time_ms": processing_time_ms,
            "model_filename": model_filename,
            "config": config,
            "source": row.get("source", "user"),
            "status": result["status"],
            "error_message": result.get("error_message"),
            "input_data": result["input_data"],
        }

        logger.info(f"Completed: {message_key} in {processing_time_ms:.1f}ms")
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
            "config": row.get("config", {}),
            "source": row.get("source", "user"),
            "status": "error",
            "error_message": str(e),
            "input_data": [],
        }


def main():
    """Main entry point for the FMU Runner service."""
    logger.info("FMU Runner Service Starting")
    logger.info(f"FMU Path: {FMU_PATH}")

    app = Application(
        consumer_group=os.getenv("CONSUMER_GROUP", "fmu-runner"),
        auto_create_topics=True,
        auto_offset_reset=os.getenv("AUTO_OFFSET_RESET", "earliest")
    )

    input_topic_name = os.environ.get("input", "simulation")
    output_topic_name = os.environ.get("output", "simulation-results")

    logger.info(f"Input topic: {input_topic_name}, Output topic: {output_topic_name}")

    input_topic = app.topic(name=input_topic_name)
    output_topic = app.topic(name=output_topic_name)

    sdf = app.dataframe(topic=input_topic)
    sdf = sdf.filter(lambda row: should_process(row.get("model_filename", "")))
    sdf = sdf.apply(process_message)
    sdf = sdf.filter(lambda row: row is not None)
    sdf.to_topic(output_topic)

    logger.info("Starting Kafka consumer...")
    app.run()


if __name__ == "__main__":
    main()
