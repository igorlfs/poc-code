import plotly.express as px
from dash import dcc, html
from pandas import DataFrame
from plotly.graph_objs import Figure

from src.colors import CRUST, GREEN, RED, WHITE
from src.layout.components.subgroups.util import extract_subgroup_limits

RECTANGLE_LINE_WIDTH = 2.0

# Rectangle displacement, estimated from someone eles's head
DELTA = 0.02


def plot_graph_and_subgroups(
    dataset_with_errors_df: DataFrame,
    x_column: str,
    y_column: str,
    subgroups: DataFrame | None,
    target_column: str = "target",
) -> Figure | html.Div:
    figure = render_graph_and_subgroups(
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
                "justifyContent": "center",
                "alignItems": "center",
                "marginTop": "2%",
                "marginBottom": "4%",
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


def render_graph_and_subgroups(
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

    render_subgroups(subgroups, dataset_with_errors_df, x_column, y_column, fig)

    return fig


def render_subgroups(
    subgroups: DataFrame,
    dataset_df: DataFrame,
    x_column: str,
    y_column: str,
    fig: Figure,
) -> None:
    for subgroups_tuple in subgroups.itertuples(index=False):
        subgroup, mean_sg, mean_dataset = subgroups_tuple

        rule1, rule2 = extract_subgroup_limits(subgroup, dataset_df, x_column, y_column)

        color = RED if mean_sg > mean_dataset else GREEN

        if rule1.attribute_name == x_column:
            x_init = rule1.lower_bound - DELTA
            y_init = rule2.lower_bound - DELTA
            width = rule1.upper_bound - rule1.lower_bound + 2 * DELTA
            height = rule2.upper_bound - rule2.lower_bound + 2 * DELTA
        else:
            x_init = rule2.lower_bound - DELTA
            y_init = rule1.lower_bound - DELTA
            width = rule2.upper_bound - rule2.lower_bound + 2 * DELTA
            height = rule1.upper_bound - rule1.lower_bound + 2 * DELTA

        fig.add_shape(
            type="rect",
            x0=x_init,
            y0=y_init,
            x1=x_init + width,
            y1=y_init + height,
            line={
                "color": color,
                "width": RECTANGLE_LINE_WIDTH,
            },
        )
        fig.add_annotation(
            x=x_init,
            y=y_init,
            text=round(mean_sg, 4),
            showarrow=False,
            xanchor="right",
            yanchor="top",
        )
        fig.add_annotation(
            x=x_init + width,
            y=y_init + height,
            text=round(mean_dataset, 4),
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
        )
