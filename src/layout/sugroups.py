from typing import Iterable

import plotly.express as px
import pysubgroup as ps
from dash import dcc, html
from pandas import DataFrame
from plotly.graph_objs import Figure

from src.colors import CRUST, WHITE

message_for_not_implemented_exception = "I still can't deal with non numeric features!"


def subgroups(
    dataset_df: DataFrame,
    x_column: str,
    y_column: str,
    target: Iterable,
    subgroups: DataFrame | None,
) -> Figure | html.Div:
    figure = generate_subgroups(
        data=dataset_df,
        x_column=x_column,
        y_column=y_column,
        target=target,
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
                "margin-bottom": "5%",
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
def generate_subgroups(  # noqa: C901, PLR0915, PLR0912
    data: DataFrame,
    x_column: str,
    y_column: str,
    target: Iterable,
    subgroups: DataFrame | None,
) -> Figure:
    classes = (
        "setosa" if x == 0 else "versicolor" if x == 1 else "virginica" for x in target
    )
    fig = px.scatter(
        data,
        x=x_column,
        y=y_column,
        color=[str(x) for x in classes],
        color_discrete_sequence=[
            "#89b4fa",
            "#a6e3a1",
            "#eba0ac",
            "#f9e2af",
            "#cba6f7",
            "#89dceb",
            "#f38ba8",
            "#fab387",
        ],
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

    rectangle_line_width = 2.0

    # Rectangle displacement, estimated from my head
    delta = 0.02
    for subgroup in subgroups.itertuples(index=False):
        # extract the subgroup limits
        rules = subgroup.subgroup.selectors
        if len(rules) < 2:  # noqa: PLR2004
            rule = rules[0]
            if isinstance(rule, ps.IntervalSelector):
                rule1_upperbound = rule.upper_bound
                rule1_lowerbound = rule.lower_bound
                rule1_attribute = rule.attribute_name
                if rule1_lowerbound == float("-inf"):
                    rule1_lowerbound = data[rule1_attribute].min()
                if rule1_upperbound == float("inf"):
                    rule1_upperbound = data[rule1_attribute].max()
            rule2_attribute = y_column if rule1_attribute == x_column else x_column
            rule2_lowerbound = data[rule2_attribute].min()
            rule2_upperbound = data[rule2_attribute].max()
        else:
            rule1, rule2 = subgroup.subgroup.selectors
            if isinstance(rule1, ps.IntervalSelector):
                rule1_upperbound = rule1.upper_bound
                rule1_lowerbound = rule1.lower_bound
                rule1_attribute = rule1.attribute_name
                if rule1_lowerbound == float("-inf"):
                    rule1_lowerbound = data[rule1_attribute].min()
                if rule1_upperbound == float("inf"):
                    rule1_upperbound = data[rule1_attribute].max()
            else:
                raise NotImplementedError(message_for_not_implemented_exception)
            if isinstance(rule2, ps.IntervalSelector):
                rule2_upperbound = rule2.upper_bound
                rule2_lowerbound = rule2.lower_bound
                rule2_attribute = rule2.attribute_name
                if rule2_lowerbound == float("-inf"):
                    rule2_lowerbound = data[rule2_attribute].min()
                if rule2_upperbound == float("inf"):
                    rule2_upperbound = data[rule2_attribute].max()
            else:
                raise NotImplementedError(message_for_not_implemented_exception)

        # draw a red or green rectangle around the region of interest
        color = "red" if subgroup.mean_sg > subgroup.mean_dataset else "green"
        if rule1_attribute == x_column:
            x0 = rule1_lowerbound - delta
            y0 = rule2_lowerbound - delta
            width = rule1_upperbound - rule1_lowerbound + 2 * delta
            height = rule2_upperbound - rule2_lowerbound + 2 * delta
            fig.add_shape(
                type="rect",
                x0=x0,
                y0=y0,
                x1=x0 + width,
                y1=y0 + height,
                line={"color": color, "width": rectangle_line_width},
            )
            fig.add_annotation(
                x=x0,
                y=y0,
                text=round(subgroup.mean_sg, 4),
                showarrow=False,
                xanchor="right",
                yanchor="top",
            )

            fig.add_annotation(
                x=x0 + width,
                y=y0 + height,
                text=round(subgroup.mean_dataset, 4),
                showarrow=False,
                xanchor="left",
                yanchor="bottom",
            )
        else:
            x0 = rule2_lowerbound - delta
            y0 = rule1_lowerbound - delta
            width = rule2_upperbound - rule2_lowerbound + 2 * delta
            height = rule1_upperbound - rule1_lowerbound + 2 * delta
            fig.add_shape(
                type="rect",
                x0=x0,
                y0=y0,
                x1=x0 + width,
                y1=y0 + height,
                line={"color": color, "width": rectangle_line_width},
            )
            fig.add_annotation(
                x=x0,
                y=y0,
                text=round(subgroup.mean_sg, 4),
                showarrow=False,
                xanchor="right",
                yanchor="top",
            )
            fig.add_annotation(
                x=x0 + width,
                y=y0 + height,
                text=round(subgroup.mean_dataset, 4),
                showarrow=False,
                xanchor="left",
                yanchor="bottom",
            )
    return fig
