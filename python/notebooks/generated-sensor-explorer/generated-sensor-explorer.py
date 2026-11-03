"""Sensor data explorer: summary table and chart on generated data.

The data is random and made in the notebook. It needs no data source.
"""

import quixlab as ql

canvas = ql.Canvas(title="Sensor data explorer")


@canvas.cell(position=(60, 0), size=(900, 100), code_height=200)
def inputs_check():
    try:
        import numpy  # noqa: F401
        import pandas  # noqa: F401
    except ImportError as exc:
        return ql.ui.markdown(f"**A package is missing:** `{exc.name}`. Add it to this notebook, then run it again.")
    return ql.ui.markdown("Ready. This notebook makes its own data. It needs no table or topic.")


@canvas.dataset(position=(60, 120), size=(900, 320), code_height=200)
def readings(inputs_check):
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(42)
    n = 500
    return pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=n, freq="min"),
        "sensor": rng.choice(["A", "B", "C"], n),
        "temperature": 20 + rng.normal(0, 2, n).cumsum() / 10,
    })


@canvas.cell(position=(60, 460), size=(440, 300), code_height=200, viz={"type": "table"})
def per_sensor(readings):
    return readings.groupby("sensor")["temperature"].agg(["count", "mean", "min", "max"]).reset_index()


@canvas.cell(position=(520, 460), size=(440, 300), code_height=200, viz={"type": "line", "x": "time", "y": "temperature"})
def trend(readings):
    return readings[readings["sensor"] == "A"]


if __name__ == "__main__":
    canvas.serve()
