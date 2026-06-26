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
    """Partially mask a secret for logging: reveal the first and last couple of chars so the
    *expected* value can be confirmed, without ever printing the whole secret."""
    if not value:
        return "<empty>"
    if len(value) <= 4:
        return value[0] + "***"
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

# Keep resolution observable for a while instead of exiting after one message: emit a
# heartbeat every HEARTBEAT_INTERVAL_SECONDS until HEARTBEAT_COUNT have been sent, then
# finish cleanly. Both are configurable (default: a beat every 5s, 12 times = ~1 minute).
heartbeat_interval = float(os.getenv("HEARTBEAT_INTERVAL_SECONDS", "5"))
heartbeat_count = int(os.getenv("HEARTBEAT_COUNT", "12"))

app = Application(consumer_group="variables-demo", auto_create_topics=True)
output_topic = app.topic(topic_name)

with app.get_producer() as producer:
    for beat in range(1, heartbeat_count + 1):
        payload = {
            "ts": int(time.time() * 1000),
            "heartbeat": beat,
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
        log.info("Published heartbeat %d/%d to topic '%s'", beat, heartbeat_count, topic_name)
        if beat < heartbeat_count:
            time.sleep(heartbeat_interval)

log.info("Variables demo complete - emitted %d heartbeats.", heartbeat_count)
