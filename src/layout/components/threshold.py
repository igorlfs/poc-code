from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate
from dash.html import Div
from pandas import DataFrame
from plotly.graph_objs import Figure
from pysubgroup import Conjunction

from src.colors import WHITE
from src.layout.components.dendrogram import generate_dendrogram_figure
from src.layout.components.util import get_clustering


def generate_decimals(a: float, b: float) -> list[float]:
    decimals = [a]
    step = 0.1
    current = a + step

    while current < b:
        decimals.append(round(current, 1))
        current += step

    return [*decimals, b]


def _filter(subgroup: Conjunction, x_column: str, y_column: str) -> bool:
    x: str = subgroup.selectors[0].attribute_name
    y: str = subgroup.selectors[1].attribute_name
    return (x == x_column and y == y_column) ^ (y == x_column and x == y_column)


def extract_first_subgroup_and_filter(
    current_class_df: DataFrame,
    selected_subgroups: list[str],
    current_groups: set[Conjunction] | list[Conjunction],
) -> list[str]:
    # get first subgroup cause it is the only one
    first_subgroup_filter = current_class_df["subgroup"].apply(
        lambda x: str(x) == selected_subgroups[0]
    )
    first_subgroup = current_class_df.loc[first_subgroup_filter]

    # get first line cause it's the only one
    columns = first_subgroup.iloc[0].to_dict()

    subgroups_filtered = filter(
        lambda sg: _filter(sg, columns["x_column"], columns["y_column"]),
        current_groups,
    )

    return [str(x) for x in list(subgroups_filtered)]


@callback(
    Output("slider-threshold", "value"),
    Input("clear-threshold-button", "n_clicks"),
)
def click_clear_threshold(_: int) -> None:
    return None


@callback(Output("clear-threshold-button", "style"), Input("slider-threshold", "value"))
def show_clear_button(pos_x: float | None) -> dict:
    if pos_x is None:
        return {"display": "none"}
    return {}


def threshold(subgroups_df: DataFrame, min_x: float, max_x: float) -> Div:  # noqa: C901
    @callback(Output("dendrogram-graph", "figure"), Input("slider-threshold", "value"))
    def display_graph(pos_x: float | None) -> Figure:
        return generate_dendrogram_figure(subgroups_df, pos_x)[0]

    @callback(
        Output("subgroups-dropdown", "options"),
        Input("slider-threshold", "value"),
        Input("subgroups-dropdown", "value"),
    )
    def filter_subgroups(pos_x: float, selected_subgroups: list[str]) -> list[str]:
        all_subgroups = subgroups_df["subgroup"].tolist()

        if pos_x is None:
            if len(selected_subgroups) == 0:
                return [str(x) for x in all_subgroups]

            if len(selected_subgroups) > 1:
                raise PreventUpdate

            return extract_first_subgroup_and_filter(
                subgroups_df, selected_subgroups, all_subgroups
            )

        clustering, _ = get_clustering(subgroups_df)

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

            if subgroups_df.loc[j, "quality"] > subgroups_df.loc[k, "quality"]:
                dict_nodes[i] = j
                subgroup_replacements[subgroups_df.loc[k, "subgroup"]] = (
                    subgroups_df.loc[j, "subgroup"]
                )
            else:
                dict_nodes[i] = k
                subgroup_replacements[subgroups_df.loc[j, "subgroup"]] = (
                    subgroups_df.loc[k, "subgroup"]
                )

        filtered_subgroups = set(subgroup_replacements.values()) - set(
            subgroup_replacements.keys()
        )

        filtered_subgroups_strings = [str(x) for x in filtered_subgroups]

        if len(selected_subgroups) == 0:
            return filtered_subgroups_strings

        if len(selected_subgroups) > 1:
            raise PreventUpdate

        return extract_first_subgroup_and_filter(
            subgroups_df, selected_subgroups, filtered_subgroups
        )

    interval_splits = generate_decimals(min_x, max_x)

    return Div(
        className="flex justify-center items-center mt-8",
        children=[
            html.H3(
                "Threshold",
                className=f"font-medium rounded-lg text-[{WHITE}] uppercase",
            ),
            dcc.Slider(
                id="slider-threshold",
                className="w-[60%]",
                value=None,
                min=min_x,
                max=max_x,
                step=0.01,
                marks={i: f"{i:.2f}" for i in interval_splits},
            ),
            html.Button(
                style={"display": "none"},
                className="mx-3 text-center font-[16pt] font-bold p-2 rounded-lg cursor-pointer uppercase",
                children=["Clear"],
                id="clear-threshold-button",
            ),
        ],
    )
