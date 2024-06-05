from dash.dcc import Graph
from dash.html import Div
from pandas import DataFrame
from plotly.graph_objs import Figure

from src.colors import BACKGROUND, CRUST, GREEN, RED, WHITE
from src.layout.components.subgroups.util import extract_subgroup_limits

RECTANGLE_LINE_WIDTH = 2.5


def plot_graph_and_subgroups(
    dataset_with_errors_df: DataFrame,
    x_column: str,
    y_column: str,
    subgroups: DataFrame | None,
    target_column: str = "target",
) -> Figure | Div:
    fig = render_graph_and_subgroups(
        dataset_with_errors_df,
        x_column,
        y_column,
        target_column,
        subgroups,
    )

    # First plot should create html.Div with no plot
    if subgroups is None:
        return Div(
            className="flex justify-center mt-10 mb-20",
            children=[
                Graph(
                    id="subgroups-plot",
                    figure=fig,
                    className="w-[80%] aspect-[2]",
                ),
            ],
        )

    # Every subsequent render call should just return the figure to update the plot
    return fig


def render_graph_and_subgroups(
    dataset_with_errors_df: DataFrame,
    x_column: str,
    y_column: str,
    target_column: str,
    subgroups: DataFrame | None,
) -> Figure:
    colors_list = [
        ["#89b4fa", "#1e66f5"],
        ["#f9e2af", "#df8e1d"],
        ["#cba6f7", "#8839ef"],
        ["#f38ba8", "#d20f39"],
        ["#a6e3a1", "#40a02b"],
        ["#fab387", "#fe640b"],
        ["#89dceb", "#04a5e5"],
        ["#eba0ac", "#e64553"],
    ]
    fig = Figure()
    for class_index, class_name in enumerate(
        dataset_with_errors_df[target_column].unique()
    ):
        class_df = dataset_with_errors_df.query(f"{target_column} == '{class_name}'")
        errors = class_df[class_name].tolist()
        colors = colors_list[class_index % len(colors_list)]
        fig.add_scatter(
            x=class_df[x_column],
            y=class_df[y_column],
            name=f"{class_name}",
            text=errors,
            mode="markers",
            marker={
                "size": 10,
                "color": errors,
                "colorscale": colors,
            },
        )

    fig.update_xaxes(title=x_column)
    fig.update_yaxes(title=y_column)

    fig.update_layout(
        font_color=WHITE,
        plot_bgcolor=CRUST,
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )

    # if subgroup is None, plot only the data
    if subgroups is None:
        return fig

    render_subgroups(subgroups, dataset_with_errors_df, x_column, fig)

    return fig


def render_subgroups(
    subgroups: DataFrame,
    dataset_df: DataFrame,
    x_column: str,
    fig: Figure,
) -> None:
    for subgroups_tuple in subgroups.itertuples(index=False):
        subgroup, mean_subgroup, mean_dataset = subgroups_tuple

        rule1, rule2, attribute = extract_subgroup_limits(subgroup, dataset_df)

        color = RED if mean_subgroup > mean_dataset else GREEN

        if attribute == x_column:
            x_init = rule1.lower
            y_init = rule2.lower
            width = rule1.upper - rule1.lower
            height = rule2.upper - rule2.lower
        else:
            x_init = rule2.lower
            y_init = rule1.lower
            width = rule2.upper - rule2.lower
            height = rule1.upper - rule1.lower

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
            text=f"<b>{round(mean_subgroup, 4)}</b>",
            bgcolor=BACKGROUND,
            showarrow=False,
            xanchor="right",
            yanchor="top",
        )
        fig.add_annotation(
            x=x_init + width,
            y=y_init + height,
            text=f"<b>{round(mean_dataset, 4)}</b>",
            bgcolor=BACKGROUND,
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
        )
