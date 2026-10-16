import math
import os
import sys
import time

from quixstreams import Application

# simulink_model_example.slx with theta = pi/4: x_new = x*cos - y*sin (M1),
# y_new = x*sin + y*cos (M2), where cos(pi/4) = 0.7071067811865476 and
# sin(pi/4) = 0.7071067811865475.
EXPECTED = [
    {"x": 1.0, "y": 0.0, "x_new": 0.7071067811865476, "y_new": 0.7071067811865475},
    {"x": 0.0, "y": 1.0, "x_new": -0.7071067811865475, "y_new": 0.7071067811865476},
    {"x": -2.0, "y": 0.0, "x_new": -1.4142135623730951, "y_new": -1.414213562373095},
]


def matches(row, expected):
    return all(
        math.isclose(row[k], expected[k], rel_tol=0, abs_tol=1e-9) for k in expected
    )


def main():
    app = Application(
        broker_address=os.environ["Quix__Broker__Address"],
        consumer_group=f"test-consumer-{int(time.time())}",
        auto_offset_reset="earliest",
    )
    app.dataframe(app.topic(os.environ["TEST_OUTPUT_TOPIC"]))

    received = app.run(timeout=float(os.environ["TEST_TIMEOUT"]), count=len(EXPECTED))
    print(f"Received: {received}")

    missing = [e for e in EXPECTED if not any(matches(r, e) for r in received)]
    if len(received) != len(EXPECTED) or missing:
        sys.exit(f"FAILED: expected {EXPECTED}, missing {missing}")

    print(f"SUCCESS: {len(received)} rotated vectors match")


if __name__ == "__main__":
    main()
