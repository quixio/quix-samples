import json
import logging
import os
import time

# For local dev, load env vars from a .env file (does not override real env vars).
from dotenv import load_dotenv
from quixstreams import Application

load_dotenv(override=False)

# Resolve the log level defensively: an unrecognized LOG_LEVEL (e.g. a typo) must
# not crash the container at startup, so fall back to INFO.
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("variables-demo")


def mask(value: str) -> str:
    """Mask a secret value for logging, keeping just enough to spot-check it resolved."""
    if not value:
        return "<empty>"
    if len(value) <= 4:
        return "***"
    return f"{value[:2]}***{value[-2:]}"


# --- Project Variables ---------------------------------------------------------
# A ProjectVariable reference is resolved by the backend to the variable's value
# before the container starts, so we read it as a normal environment variable.
# API_REGION is non-secret; API_SECRET is delivered via a Kubernetes secret.
api_region = os.getenv("API_REGION", "")
api_secret = os.getenv("API_SECRET", "")

# --- Variable Group ------------------------------------------------------------
# The backend expands the selected value set of the group into individual env
# vars matching the keys declared in library.json. All members here are non-secret.
influx_host = os.getenv("INFLUXDB_HOST", "")
influx_port = os.getenv("INFLUXDB_PORT", "")
influx_org = os.getenv("INFLUXDB_ORG", "")

# Read every resolved value once, then reuse it for both logging and the
# missing-variable check so the two can never drift apart.
api_secret_masked = mask(api_secret)
values = {
    "API_REGION": api_region,
    "API_SECRET": api_secret,
    "INFLUXDB_HOST": influx_host,
    "INFLUXDB_PORT": influx_port,
    "INFLUXDB_ORG": influx_org,
}

# Log every resolved value so injection can be verified from the deployment logs.
# Only the secret project variable is masked.
resolved = dict(values, API_SECRET=api_secret_masked)
log.info("Resolved variables from backend: %s", json.dumps(resolved))

# Warn on any required value that did not resolve (e.g. a missing prerequisite).
missing = [k for k, v in values.items() if not v]
if missing:
    log.warning("Missing required variables after resolution: %s", missing)

# 'output' is a hard deploy-time prerequisite (no topic means nothing to produce
# to), unlike the resolved variables above which are observational and only warn.
topic_name = os.getenv("output")
if not topic_name:
    raise ValueError("The 'output' environment variable is required.")

# Emit a single heartbeat so successful resolution is visible on the output topic too.
app = Application(consumer_group="variables-demo", auto_create_topics=True)
output_topic = app.topic(topic_name)

with app.get_producer() as producer:
    payload = {
        "ts": int(time.time() * 1000),
        "api_region": api_region,
        "api_secret_masked": api_secret_masked,
        "influxdb_host": influx_host,
        "influxdb_port": influx_port,
        "influxdb_org": influx_org,
    }
    producer.produce(
        topic=output_topic.name,
        key="variables-demo",
        value=json.dumps(payload).encode("utf-8"),
    )
    log.info("Published heartbeat to topic '%s'", topic_name)
