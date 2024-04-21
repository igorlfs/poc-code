from typing import Iterable

import plotly.express as px
import pysubgroup as ps
from dash import dcc, html
from pandas import DataFrame
from plotly.graph_objs import Figure

from src.colors import CRUST, WHITE

message_for_not_implemented_exception = "I still can't deal with non numeric features!"


def subgroups(
    dataset_with_errors_df: DataFrame,
    x_column: str,
    y_column: str,
    subgroups: DataFrame | None,
    target_column: str = "target",
) -> Figure | html.Div:
    figure = generate_subgroups(
        dataset_with_errors_df,
        x_column,
        y_column,
        target_column,
        subgroups=subgroups,
    )

    # First plot should create html.Div with no plot
    if subgroups is None:
        return html.Div(
            className="subgroups-2d-plot",
            style={
                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "margin-top": "2%",
                "margin-bottom": "4%",
            },
            children=[
                dcc.Graph(
                    id="subgroups-plot",
                    figure=figure,
                    style={
                        "width": "1400px",
                        "height": "700px",
                    },
                ),
            ],
        )

    # Every subsequent render call should just return the figure to update the plot
    return figure


# Plot a 2D scatterplot showing the samples, its classes, and the subgroups passed as parameters
# to the functio
# TODO simplify function
def generate_subgroups(
    dataset_with_errors_df: DataFrame,
    x_column: str,
    y_column: str,
    target_column: str,
    subgroups: DataFrame | None,
) -> Figure:
    classes = dataset_with_errors_df[target_column].tolist()
    errors = [
        row[classes[i]] for i, (_, row) in enumerate(dataset_with_errors_df.iterrows())
    ]

    fig = px.scatter(
        dataset_with_errors_df,
        x=x_column,
        y=y_column,
        color=errors,
        color_continuous_scale=[
            "#df8e1d",
            "#8839ef",
        ],
    )
    fig.update_traces(
        marker={
            "size": 10,
        },
    )
    fig.update_layout(
        font_color=WHITE,
        plot_bgcolor=CRUST,
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )

    # if subgroup is None, plot only the data
    if subgroups is None:
        return fig

    return fig
