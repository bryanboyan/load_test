import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.graph_objs import Figure
from tests.Config import config

# Note: Make sure you configure the config.yaml to specify the tasks.
tasks = config.get_tasks()
DATA_FOLDER = "data" # if data/ folder is poisoned, can use data/bakup folder
LATENCY_PERCENTILES = [.5, .75, .95, .99]

def build_request_dataframes() -> dict[str,pd.DataFrame]:
    df_requests = {}
    for task in tasks:
        df_task = pd.read_csv(
                f"{DATA_FOLDER}/request_{task}.csv",
                header=None,
                names=["timestamp"],
            )
        if df_task.empty:
            raise FileNotFoundError(f"request_{task}.csv is empty")
        df_task["timestamp"] = pd.to_datetime(df_task["timestamp"], unit="s")
        df_task.set_index("timestamp", inplace=True)
        df_task = df_task.resample('s').size().to_frame('count')
        df_requests[task] = df_task
    return df_requests

def build_response_dataframes() -> dict[str,pd.DataFrame]:
    df_responses = {}
    for task in tasks:
        df_task = pd.read_csv(
                f"{DATA_FOLDER}/response_{task}.csv",
                header=None,
                names=["timestamp", "status", "data"],
            )
        if df_task.empty:
            raise FileNotFoundError(f"{task}.csv is empty")
        df_task["timestamp"] = pd.to_datetime(df_task["timestamp"], unit="s")
        df_task.set_index("timestamp", inplace=True)
        successes = df_task[df_task["status"] == "success"]
        
        latency_percentiles = successes["data"].resample('10s').quantile(LATENCY_PERCENTILES).unstack()
        
        failures = df_task[df_task["status"] == "failure"]
        failure_counts = failures.resample("s").size()
        qps = df_task.resample("s").size()
        failure_rate = failure_counts / qps
        failure_rate = failure_rate.fillna(0)
        
        
        df_responses[task] = latency_percentiles, failure_rate
    return df_responses


def get_xaxes_range(
    df_responses: dict[str, pd.DataFrame], df_requests: dict[str, pd.DataFrame]
) -> tuple[pd.Timestamp, pd.Timestamp]:
    min_list, max_list = [], []
    for task in tasks:
        pct, fr = df_responses[task]
        min_list.append(min(min(df_requests[task].index), min(pct.index), min(fr.index)))
        max_list.append(max(max(df_requests[task].index), max(pct.index), max(fr.index)))
    return min(min_list), max(max_list)


def build_figure(
    df_responses: dict[str, pd.DataFrame], df_requests: dict[str, pd.DataFrame]
) -> Figure:
    fig = make_subplots(
        rows=len(df_responses) + 1,
        cols=1,
        specs=[[{"secondary_y": True}]] * len(df_responses) + [[{}]],
        shared_xaxes=True,
        subplot_titles=[f"{task} Performance" for task in df_responses.keys()] + ["Load"]
    )

    row_index = 1 # index start from 1
    # Add latency and failure_rate graphs
    for task, df_res in df_responses.items():
        latency_percentiles, failure_rate = df_res
        # latency percentiles
        for pc in LATENCY_PERCENTILES:
            fig.add_trace(
                go.Scatter(
                    x=latency_percentiles.index,
                    y=latency_percentiles[pc],
                    name=f"{task} {pc} Latency",
                    hovertemplate="%{y}",
                    yaxis=f"y{row_index}",
                ),
                row=row_index,
                col=1,
                secondary_y=False,
            )
        fig.update_yaxes(
            title_text="Latency (seconds)",
            tickformat='.4f',
            row=row_index,
            col=1,
            secondary_y=False
        )

        # failure rate y-axis
        fig.add_trace(
            go.Scatter(
                x=failure_rate.index,
                y=failure_rate,
                name=f"{task} Failure Rate",
                hovertemplate="%{y}",
                yaxis=f"y{row_index}",
            ),
            row=row_index,
            col=1,
            secondary_y=True,
        )
        max_failure_rate = max(max(failure_rate), 0.1)  # max failure rate or 10% as higher bound
        fig.update_yaxes(
            title_text="Failure Rate (%)",
            range=[0, max_failure_rate],
            tickformat=".0%",
            row=row_index,
            col=1,
            secondary_y=True,
        )

        fig.update_xaxes(showticklabels=True, row=row_index, col=1)

        row_index += 1

    # Add threads graph
    for task in tasks:
        task_df = df_requests[task]
        fig.add_trace(
            go.Scatter(
                x=task_df.index,
                y=task_df["count"],
                name=f"{task} rps",
                hovertemplate="%{y}",
                yaxis=f"y{row_index}",
            ),
            row=row_index,
            col=1,
        )
    fig.update_yaxes(title_text="Req per Second", row=row_index, col=1, secondary_y=False)

    min_timestamp, max_timestamp = get_xaxes_range(df_responses, df_requests)
    fig.update_layout(
        xaxis=dict(range=[min_timestamp, max_timestamp]), hovermode="x unified", title="Load Test Analysis"
    )
    fig.update_xaxes(tickformat="%H:%M:%S")

    return fig


if __name__ == "__main__":
    df_requests = build_request_dataframes()
    df_responses = build_response_dataframes()
    fig = build_figure(df_responses, df_requests)
    fig.show()
