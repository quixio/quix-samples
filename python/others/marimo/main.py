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
    import json
    import urllib.request

    def get_live_token():
        # Fetch the live owner token from the in-pod auth proxy so every API
        # call uses a fresh token (the injected env token can go stale).
        # Falls back to the static SDK token when the proxy is unavailable
        # (e.g. running standalone or before first login).
        try:
            with urllib.request.urlopen(
                "http://127.0.0.1:8082/internal-token", timeout=2
            ) as response:
                token = json.loads(response.read().decode("utf-8")).get("token")
                if token:
                    return token
        except Exception as e:
            print(f"live-token fetch failed, falling back to env token: {e}")
        # Fallback: injected SDK token (standalone / before first login).
        token = os.environ.get("Quix__Sdk__Token")
        if not token:
            raise RuntimeError(
                "No Quix token available: the auth proxy is unreachable and "
                "Quix__Sdk__Token is not set."
            )
        return token

    client = QuixLakeClient(
        base_url=os.environ["Quix__Lakehouse__Query__Url"],
        token_provider=get_live_token,
    )
    return client, get_live_token


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


@app.cell
def _(mo):
    mo.md(r"""## Live-user blob storage""")
    return


@app.cell
def _(get_live_token, os):
    from quix_blob import scope_connection_to_live_user
    from quixportal import get_filesystem

    def _blob_filesystem():
        # The platform injects the bound blob connection here; the gateway scopes
        # blob access to the live user when the access key is their user id and
        # the secret is their token.
        connection_json = os.environ.get("Quix__BlobStorage__Connection__Json")
        user_id = os.environ.get("Quix__DevSession__UserId")
        if not connection_json or not user_id:
            print(
                "blob storage: bound connection or Quix__DevSession__UserId "
                "missing; skipping live-user filesystem."
            )
            return None
        os.environ["Quix__BlobStorage__Connection__Json"] = (
            scope_connection_to_live_user(
                connection_json, user_id, get_live_token()
            )
        )
        return get_filesystem()

    fs = _blob_filesystem()
    fs.ls("/") if fs is not None else "blob storage unavailable"
    return (fs,)


if __name__ == "__main__":
    app.run()
