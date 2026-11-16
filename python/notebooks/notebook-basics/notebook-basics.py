"""Notebook basics: a note, a Python cell, a table and a chart on generated data.

The data is random and made in the notebook. It needs no data source.
"""

import quixlab as ql

canvas = ql.Canvas(title="Notebook basics")


@canvas.cell(position=(60, 0), size=(900, 230), code_height=80)
def note():
    return ql.ui.markdown("**Notebook basics.** Each box is a cell. Change the code of a cell and run it again.")


@canvas.dataset(position=(60, 250), size=(900, 380), code_height=120)
def numbers(note):
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(7)
    n = 100
    return pd.DataFrame({"step": range(n), "value": rng.normal(0, 1, n).cumsum()})


@canvas.cell(position=(60, 650), size=(440, 360), code_height=100, viz={"type": "table"})
def summary(numbers):
    return numbers["value"].describe().reset_index()


@canvas.cell(position=(520, 650), size=(440, 360), code_height=100, viz={"type": "line", "x": "step", "y": "value"})
def chart(numbers):
    return numbers
