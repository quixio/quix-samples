# /// script
# [tool.marimo.display]
# theme = "dark"
# ///

import marimo

__generated_with = "0.16.4"
app = marimo.App(width="full")


@app.cell
def _():
    import os
    import marimo as mo
    return mo, os


@app.cell
def _():
    from quixlake import QuixLakeClient
    return (QuixLakeClient,)


@app.cell
def _(mo):
    mo.md(r"""## Query QuixLake Data""")
    return


@app.cell
def _(QuixLakeClient, os):
    # TODO: Replace with your QuixLake URL
    QUIXLAKE_URL = "https://your-quixlake-instance.quix.io"

    client = QuixLakeClient(
        base_url=QUIXLAKE_URL,
        token=os.environ["Quix__Sdk__Token"]
    )
    return (client,)


@app.cell
def _(mo):
    # TODO: Modify the SQL query for your data
    default_query = """
SELECT
    Timestamp as time,
    value
FROM your_table
ORDER BY Timestamp
LIMIT 1000
""".strip()

    sql_form = mo.ui.code_editor(
        value=default_query,
        language="sql",
        label="SQL query",
        min_height=150,
    ).form(submit_button_label="Run SQL")

    sql_form
    return (sql_form,)


@app.cell
def _(client, sql_form):
    df = client.query(sql_form.value)
    df
    return (df,)


@app.cell
def _(df, mo):
    import plotly.express as px
    fig = px.line(
        df,
        x="time",
        y="value",
        title="Waveform",
    )
    mo.ui.plotly(fig)
    return


if __name__ == "__main__":
    app.run()
