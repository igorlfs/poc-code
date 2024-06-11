from dash import Dash, Input, Output, dcc, html
from dash.exceptions import PreventUpdate
from dash.html import Div
from pandas import DataFrame
from plotly.graph_objs import Figure
from pysubgroup import Conjunction

from src.colors import WHITE
from src.layout.components.dendrogram import generate_dendrogram_figure
from src.layout.components.util import get_clustering


def threshold(  # noqa: C901
    app: Dash,
    subgroups_df: DataFrame,
    current_class: str,
) -> Div:
    @app.callback(
        Output("slider-threshold", "value"),
        Input("clear-threshold-button", "n_clicks"),
    )
    def click_clear_threshold(_: int) -> None:
        return None

    @app.callback(
        Output("clear-threshold-button", "style"), Input("slider-threshold", "value")
    )
    def show_clear_button(pos_x: float | None):
        if pos_x is None:
            return {"display": "none"}
        return {}

    @app.callback(
        Output("dendrogram-graph", "figure"), Input("slider-threshold", "value")
    )
    def display_graph(pos_x: float | None) -> Figure:
        return generate_dendrogram_figure(subgroups_df, current_class, pos_x)

    def _filter(subgroup: Conjunction, x_column: str, y_column: str) -> bool:
        x: str = subgroup.selectors[0].attribute_name
        y: str = subgroup.selectors[1].attribute_name
        return (x == x_column and y == y_column) ^ (y == x_column and x == y_column)

    @app.callback(
        Output("subgroups-dropdown", "options"),
        Input("slider-threshold", "value"),
        Input("subgroups-dropdown", "value"),
    )
    def filter_subgroups(pos_x: float, selected_subgroups: list[str]) -> list[str]:
        if pos_x is None:
            return []

        current_class_df = subgroups_df.query(f"`class` == '{current_class}'")
        clustering, _ = get_clustering(current_class_df)

        n_samples = len(clustering.labels_)
        dict_nodes = {}  # Save the representative subgroup for each merge
        subgroup_replacements = {}  # Save the original and substitute subgroups

        for i, dist in enumerate(clustering.distances_):
            if dist > pos_x:
                break

            j = (
                dict_nodes[clustering.children_[i][0] - n_samples]
                if clustering.children_[i][0] >= n_samples
                else clustering.children_[i][0]
            )
            k = (
                dict_nodes[clustering.children_[i][1] - n_samples]
                if clustering.children_[i][1] >= n_samples
                else clustering.children_[i][1]
            )

            if current_class_df.loc[j, "quality"] > current_class_df.loc[k, "quality"]:
                dict_nodes[i] = j
                subgroup_replacements[current_class_df.loc[k, "subgroup"]] = (
                    current_class_df.loc[j, "subgroup"]
                )
            else:
                dict_nodes[i] = k
                subgroup_replacements[current_class_df.loc[j, "subgroup"]] = (
                    current_class_df.loc[k, "subgroup"]
                )

        filtered_subgroups = set(subgroup_replacements.values()) - set(
            subgroup_replacements.keys()
        )

        filtered_subgroups_strings = [str(x) for x in filtered_subgroups]

        if len(selected_subgroups) == 0:
            return filtered_subgroups_strings

        if len(selected_subgroups) > 1:
            raise PreventUpdate

        # get first subgroup cause it is the only one
        first_subgroup = current_class_df.query(
            f"subgroup_str == '{selected_subgroups[0]}'"
        )[["x_column", "y_column"]]

        # get first line cause it's the only one
        columns = first_subgroup.iloc[0].to_dict()

        subgroups_filtered_and_match_columns = filter(
            lambda sg: _filter(sg, columns["x_column"], columns["y_column"]),
            filtered_subgroups,
        )

        return [str(x) for x in list(subgroups_filtered_and_match_columns)]

    return Div(
        className="flex justify-center items-center mt-8",
        children=[
            html.H3(
                "Threshold",
                className=f"font-medium rounded-lg text-[{WHITE}]",
            ),
            dcc.Slider(
                id="slider-threshold",
                className="w-[500px]",
                min=0,
                max=1,
                step=0.01,
                # No, we can't be smarter here
                # https://community.plotly.com/t/dcc-slider-right-most-label-mark-is-missing/27274
                marks={
                    0: "0",
                    0.2: "0.2",
                    0.4: "0.4",
                    0.6: "0.6",
                    0.8: "0.8",
                    1: "1",
                },
            ),
            html.Button(
                style={"display": "none"},
                className="mx-3 text-center font-[16pt] font-bold p-2 rounded-lg cursor-pointer uppercase",
                children=["Clear"],
                id="clear-threshold-button",
            ),
        ],
    )
