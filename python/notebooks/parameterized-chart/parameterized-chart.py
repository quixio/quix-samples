"""Parameterized chart: widgets change a chart.

The data is random and made in the notebook. It needs no data source.
"""

import quixlab as ql

canvas = ql.Canvas(title="Parameterized chart")


@canvas.cell(position=(60, 0), size=(900, 230), code_height=80)
def inputs_check():
    try:
        import numpy  # noqa: F401
        import pandas  # noqa: F401
    except ImportError as exc:
        return ql.ui.markdown(f"**A package is missing:** `{exc.name}`. Add it to this notebook, then run it again.")
    return ql.ui.markdown("Ready. Pick a sensor and a window size. The chart updates.")


@canvas.cell(position=(60, 250), size=(440, 230), code_height=80)
def sensor_pick(inputs_check):
    return ql.ui.dropdown(["A", "B", "C"], value="A", label="Sensor")


@canvas.cell(position=(520, 250), size=(440, 230), code_height=80)
def window_size(inputs_check):
    return ql.ui.text(label="Window (rows)", value="20")


@canvas.cell(position=(60, 500), size=(900, 380), code_height=100, viz={"type": "line", "x": "time", "y": "smooth"})
def chart_data(sensor_pick, window_size):
    import numpy as np
    import pandas as pd
    seed = {"A": 1, "B": 2, "C": 3}.get(sensor_pick.value, 1)
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=300, freq="min"),
        "value": 20 + rng.normal(0, 1, 300).cumsum() / 5,
    })
    try:
        window = max(1, int(window_size.value))
    except (TypeError, ValueError):
        window = 20
    df["smooth"] = df["value"].rolling(window, min_periods=1).mean()
    return df


if __name__ == "__main__":
    canvas.serve()
