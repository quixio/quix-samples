import json
import os
import sys
import time

from quixstreams import Application

KEY = b"test_db.test_table"
EXPECTED = [
    {
        "kind": "insert",
        "schema": "test_db",
        "table": "test_table",
        "columnnames": ["id", "name", "value"],
        "columnvalues": [1, "alice", 100],
        "oldkeys": {},
    },
    {
        "kind": "insert",
        "schema": "test_db",
        "table": "test_table",
        "columnnames": ["id", "name", "value"],
        "columnvalues": [2, "bob", 200],
        "oldkeys": {},
    },
    {
        "kind": "update",
        "schema": "test_db",
        "table": "test_table",
        "columnnames": ["id", "name", "value"],
        "columnvalues": [1, "alice", 150],
        "oldkeys": {
            "keynames": ["id", "name", "value"],
            "keyvalues": [1, "alice", 100],
        },
    },
    {
        "kind": "delete",
        "schema": "test_db",
        "table": "test_table",
        "columnnames": [],
        "columnvalues": [],
        "oldkeys": {
            "keynames": ["id", "name", "value"],
            "keyvalues": [2, "bob", 200],
        },
    },
]

app = Application(
    broker_address=os.environ["Quix__Broker__Address"],
    consumer_group="mysql-cdc-verify",
    auto_offset_reset="earliest",
)
consumer = app.get_consumer()
consumer.subscribe([os.environ["TEST_OUTPUT_TOPIC"]])
received = []


def consume(seconds, stop_at=None):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline and len(received) != stop_at:
        msg = consumer.poll(timeout=0.5)
        if msg is not None:
            received.append((msg.key(), json.loads(msg.value())))


consume(30, stop_at=len(EXPECTED))
consume(3)
consumer.close()

if received != [(KEY, value) for value in EXPECTED]:
    print(f"Expected {len(EXPECTED)} messages keyed {KEY!r}:")
    for value in EXPECTED:
        print(f"  {value}")
    print(f"Observed {len(received)}:")
    for key, value in received:
        print(f"  {key!r} {value}")
    sys.exit(1)

print("Success: 4 CDC messages (insert, insert, update, delete) verified")
