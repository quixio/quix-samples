from quixstreaming import QuixStreamingClient
from quixstreaming.app import App
from in_memory_view import InMemoryView
import os
from dash import dcc, Input, Output, Dash, html
import dash_table as dt
import dash_bootstrap_components as dbc
import threading

client = QuixStreamingClient()
input_topic = client.open_input_topic(os.environ["input"], "dashboard-5")
quix_function = QuixFunction(input_topic)


def quix_consumer():
    quix_function.start()
    App.run()

t1 = threading.Thread(target=quix_consumer)
t1.start()

external_stylesheets = [dbc.themes.FLATLY]

app = Dash(external_stylesheets=external_stylesheets)

app.layout = dbc.Container([
    html.H1("Dashboard"),
    dt.DataTable(
        id='tbl', data=quix_function.state.to_dict('records'),
        columns=[{"name": i, "id": i} for i in quix_function.state.columns],
    ),
    dcc.Interval(id="interval", interval=1000),
])


@app.callback(Output('tbl', 'data'), [Input('interval', 'n_intervals')])
def update_data(n_intervals):
    return quix_function.state.to_dict('records')

@app.callback(Output('tbl', 'columns'), [Input('interval', 'n_intervals')])
def update_columns(n_intervals):
    return [{"name": i, "id": i} for i in quix_function.state.columns]


#App.run()
app.run_server(debug=True, host="0.0.0.0", port=80)