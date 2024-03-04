import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.graph_objs import Figure
from tests.Config import config

tasks = config.get_tasks()
DATA_FOLDER = "data"

def build_load_dataframe() -> dict[str,pd.DataFrame]:
    load = pd.read_csv(
        f"{DATA_FOLDER}/load.csv", header=None, names=["timestamp", "task", "threads"]
    )
    if load.empty:
        raise FileNotFoundError("load.csv is empty")

    load["timestamp"] = pd.to_datetime(load["timestamp"], unit="s")
    df_loads = {}
    for task in tasks:
        load_task = load[load["task"] == task].copy()
        load_task.sort_values(by="timestamp", inplace=True)
        load_task.set_index("timestamp", inplace=True)
        load_task = load_task.resample("1s").ffill()
        df_loads[task] = load_task
    return df_loads

def build_task_dataframes() -> dict[str,pd.DataFrame]:
    df_tasks = {}
    for task in tasks:
        df_task = pd.read_csv(
                f"{DATA_FOLDER}/{task}.csv",
                header=None,
                names=["timestamp", "status", "data"],
            )
        if df_task.empty:
            raise FileNotFoundError(f"{task}.csv is empty")
        df_task["timestamp"] = pd.to_datetime(df_task["timestamp"], unit="s")
        df_task.set_index("timestamp", inplace=True)
        successes = df_task[df_task["status"] == "success"]
        average_latency = successes.resample("5s")["data"].mean()
        failures = df_task[df_task["status"] == "failure"]
        failure_counts = failures.resample("5s").size()
        qps = df_task.resample("5s").size()
        failure_rate = failure_counts / qps
        failure_rate = failure_rate.fillna(0)
        df_task_final = pd.DataFrame(
            {"latency": average_latency, "failure_rate": failure_rate}
        )
        df_task_final.ffill(inplace=True)
        df_tasks[task] = df_task_final
    return df_tasks


def get_xaxes_range(
    df_tasks: dict[str, pd.DataFrame], df_loads: dict[str, pd.DataFrame]
) -> tuple[pd.Timestamp, pd.Timestamp]:
    min_list, max_list = [], []
    for task in tasks:
        min_list.append(min(min(df_loads[task].index), min(df_tasks[task].index)))
        max_list.append(max(max(df_loads[task].index), max(df_tasks[task].index)))
    return min(min_list), max(max_list)


def build_figure(
    df_tasks: dict[str, pd.DataFrame], df_loads: dict[str, pd.DataFrame]
) -> Figure:
    fig = make_subplots(
        rows=len(df_tasks) + 1,
        cols=1,
        specs=[[{"secondary_y": True}]] * len(df_tasks) + [[{}]],
        shared_xaxes=True,
        subplot_titles=[f"{task} Performance" for task in df_tasks.keys()] + ["Load"]
    )

    row_index = 1 # index start from 1
    # Add latency and failure_rate graphs
    for task, df in df_tasks.items():
        # latency y-axis
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["latency"],
                name=f"{task} Latency",
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
                x=df.index,
                y=df["failure_rate"],
                name=f"{task} Failure Rate",
                yaxis=f"y{row_index}",
            ),
            row=row_index,
            col=1,
            secondary_y=True,
        )
        max_failure_rate = max(max(df["failure_rate"]), 0.1) # max failure rate or 10% as higher bound
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
        task_df = df_loads[task]
        fig.add_trace(
            go.Scatter(
                x=task_df.index,
                y=task_df["threads"],
                name=f"{task} Threads",
                yaxis=f"y{row_index}",
            ),
            row=row_index,
            col=1,
        )
    fig.update_yaxes(title_text="Threads", row=row_index, col=1, secondary_y=False)

    min_timestamp, max_timestamp = get_xaxes_range(df_tasks, df_loads)
    fig.update_layout(
        xaxis=dict(range=[min_timestamp, max_timestamp]), hovermode="x unified", title="Load Test Analysis"
    )
    fig.update_xaxes(tickformat="%H:%M:%S")

    return fig


if __name__ == "__main__":
    df_loads = build_load_dataframe()
    df_tasks = build_task_dataframes()
    fig = build_figure(df_tasks, df_loads)
    fig.show()
