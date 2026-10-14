"""
Verify that the Quix Lakehouse Sink emits stream-timeout events.

Every key produced by produce_test_data.py goes silent once the producer finishes, so after
STREAM_TIMEOUT_SECONDS the sink must have published at least one event to the timeout topic.
"""
import json
import os
import sys
import time

from quixstreams import Application


def fail(reason):
    print(f"✗ FAILED: {reason}")
    sys.exit(1)


def main():
    broker_address = os.getenv("Quix__Broker__Address", "kafka:9092")
    topic_name = os.getenv("TEST_TIMEOUT_TOPIC", "test-lakehouse-timeout")
    max_wait_seconds = 30

    print(f"Consuming stream-timeout events from topic: {topic_name}")

    app = Application(
        broker_address=broker_address,
        consumer_group="lakehouse-sink-timeout-verifier",
        auto_offset_reset="earliest",
    )

    deadline = time.monotonic() + max_wait_seconds
    with app.get_consumer() as consumer:
        consumer.subscribe([topic_name])
        while time.monotonic() < deadline:
            msg = consumer.poll(timeout=1.0)
            if msg is not None and not msg.error():
                break
        else:
            fail(f"no event on {topic_name} within {max_wait_seconds}s")

    key = msg.key().decode()
    event = json.loads(msg.value())
    print(f"Received: key={key!r} value={event}")

    if event.get("event") != "stream_timeout":
        fail(f"expected event 'stream_timeout', got {event.get('event')!r}")
    if not key.startswith("key_"):
        fail(f"expected one of the produced test keys, got {key!r}")
    if event.get("stream") != key:
        fail(f"'stream' {event.get('stream')!r} does not match the message key {key!r}")
    if not isinstance(event.get("ts_ms"), int):
        fail(f"'ts_ms' is not an integer: {event.get('ts_ms')!r}")

    print("✓ Stream-timeout event verified")


if __name__ == "__main__":
    main()
