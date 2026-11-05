"""Live lake viewer: show the latest rows of the first Quix Lake table and chart one number.

Needs at least one Quix Lake table in this workspace. Run the cells again to refresh.
"""

import quixlab as ql

canvas = ql.Canvas(title="Live lake viewer")


@canvas.cell(position=(60, 0), size=(900, 140), code_height=200)
def inputs_check():
    try:
        from quixlab.sources.lake import list_tables
        names = [t["name"] for t in list_tables() if t.get("name")]
    except Exception as exc:
        return ql.ui.markdown(f"**Quix Lake is not reachable.** Check that this workspace has Quix Lake. ({type(exc).__name__})")
    if not names:
        return ql.ui.markdown("**This workspace has no Quix Lake table yet.** Write data to a table, then run this notebook again.")
    return ql.ui.markdown(f"Ready. The first table is `{names[0]}`. Change the SQL in the next cell to use another table.")


@canvas.dataset(position=(60, 160), size=(900, 360), code_height=240)
def latest(inputs_check):
    import pandas as pd
    try:
        from quixlab.sources.lake import list_tables
        names = [t["name"] for t in list_tables() if t.get("name")]
        if not names:
            return pd.DataFrame()
        df = ql.sql(f'SELECT * FROM "{names[0]}" LIMIT 1000')
    except Exception:
        return pd.DataFrame()
    stamps = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    if stamps:
        df = df.sort_values(stamps[0], ascending=False)
    return df.head(200)


@canvas.cell(position=(60, 540), size=(900, 360), code_height=240, viz={"type": "line", "x": "time", "y": "value"})
def chart(latest):
    import pandas as pd
    if not len(latest):
        return pd.DataFrame({"time": [], "value": []})
    stamps = [c for c in latest.columns if pd.api.types.is_datetime64_any_dtype(latest[c])]
    numbers = latest.select_dtypes("number").columns
    x = latest[stamps[0]] if stamps else latest.reset_index().index
    y = latest[numbers[0]] if len(numbers) else latest.index
    return pd.DataFrame({"time": x, "value": y}).sort_values("time")


if __name__ == "__main__":
    canvas.serve()
