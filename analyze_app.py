from Analyzer import build_load_dataframe, build_task_dataframes, build_figure
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from plotly.graph_objs import Figure

app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="live-update-graph", style={"width": "100%", "height": "90vh"}),
        dcc.Interval(
            id="interval-component", interval=3_000, n_intervals=0  # in milliseconds
        ),
    ]
)


@app.callback(
    Output("live-update-graph", "figure"), Input("interval-component", "n_intervals")
)
def figure_pipeline(n) -> Figure:
    load_final = build_load_dataframe()
    df_tasks = build_task_dataframes()
    return build_figure(df_tasks, load_final)


if __name__ == "__main__":
    app.run_server(debug=True, port=8081)
