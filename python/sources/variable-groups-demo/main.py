import json
import logging
import os
import time

from dotenv import load_dotenv
from quixstreams import Application

load_dotenv(override=False)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("variable-groups-demo")


def mask(value: str) -> str:
    if not value:
        return "<empty>"
    if len(value) <= 4:
        return "***"
    return f"{value[:2]}***{value[-2:]}"


# Project Variable reference: backend resolves this to the variable's value
# before the container starts, so we just read the env var as normal.
api_key = os.getenv("API_KEY", "")

# Variable Group: the backend expands the group's selected value set into
# individual env vars matching the keys declared in library.json.
influx_host = os.getenv("INFLUXDB_HOST", "")
influx_port = os.getenv("INFLUXDB_PORT", "")
influx_token = os.getenv("INFLUXDB_TOKEN", "")

resolved = {
    "API_KEY": mask(api_key),
    "INFLUXDB_HOST": influx_host,
    "INFLUXDB_PORT": influx_port,
    "INFLUXDB_TOKEN": mask(influx_token),
}

log.info("Resolved variables from backend: %s", json.dumps(resolved))

missing = [k for k, v in resolved.items() if not v or v == "<empty>"]
if missing:
    log.error("Missing required variables after resolution: %s", missing)
    raise SystemExit(1)

topic_name = os.getenv("output")
if not topic_name:
    raise ValueError("The 'output' environment variable is required.")

app = Application(consumer_group="variable-groups-demo")
output_topic = app.topic(topic_name)

with app.get_producer() as producer:
    payload = {
        "ts": int(time.time() * 1000),
        "host": influx_host,
        "port": influx_port,
        "api_key_masked": mask(api_key),
        "token_masked": mask(influx_token),
    }
    producer.produce(
        topic=output_topic.name,
        key="variable-groups-demo",
        value=json.dumps(payload).encode("utf-8"),
    )
    log.info("Published heartbeat to topic '%s'", topic_name)
