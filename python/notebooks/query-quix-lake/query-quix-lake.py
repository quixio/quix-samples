"""Query Quix Lake: run SQL on the first table and plot it.

Needs at least one Quix Lake table in this workspace.
"""

import quixlab as ql

canvas = ql.Canvas(title="Query Quix Lake")


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


@canvas.dataset(position=(60, 160), size=(900, 360), code_height=200)
def rows(inputs_check):
    import pandas as pd
    try:
        from quixlab.sources.lake import list_tables
        names = [t["name"] for t in list_tables() if t.get("name")]
        if names:
            return ql.sql(f'SELECT * FROM "{names[0]}" LIMIT 1000')
    except Exception:
        pass
    return pd.DataFrame()


@canvas.cell(position=(60, 540), size=(900, 360), code_height=200, viz={"type": "table"})
def summary(rows):
    return rows.describe(include="all") if len(rows) else rows


if __name__ == "__main__":
    canvas.serve()
