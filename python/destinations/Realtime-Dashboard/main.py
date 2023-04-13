import quixstreams as qx
from in_memory_view import InMemoryView
import os
from dash import dcc, Input, Output, Dash, html
import dash_table as dt
import dash_bootstrap_components as dbc
import threading

client = qx.QuixStreamingClient()
consumer_topic = client.get_topic_consumer(os.environ["input"], "dashboard")
in_memory_view = InMemoryView(consumer_topic)

external_stylesheets = [dbc.themes.FLATLY]

app = Dash(external_stylesheets = external_stylesheets)

app.layout = dbc.Container([
    html.H1("Dashboard"),
    dt.DataTable(
        id='tbl', data = in_memory_view.state.to_dict('records'),
        columns=[{"name": i, "id": i} for i in in_memory_view.state.columns],
    ),
    dcc.Interval(id = "interval", interval = 1000),
])


@app.callback(Output('tbl', 'data'), [Input('interval', 'n_intervals')])
def update_data(n_intervals):
    return in_memory_view.state.to_dict('records')

@app.callback(Output('tbl', 'columns'), [Input('interval', 'n_intervals')])
def update_columns(n_intervals):
    return [{"name": i, "id": i} for i in in_memory_view.state.columns]

def web_server():  
    app.run_server(debug = False, host = "0.0.0.0", port = 80)

t1 = threading.Thread(target = web_server)
t1.start()

qx.App.run()
