from dash import Dash, Input, Output, State
from dash.dash import PreventUpdate
from dash.dcc.Dropdown import Dropdown
from dash.html import Button, Div
from pandas import DataFrame
from plotly.graph_objs import Figure
from pysubgroup import Conjunction

from src.layout.components.graph import plot_graph_and_subgroups


def subgroups_dropdown(
    app: Dash,
    dataset_with_errors_df: DataFrame,
    subgroups_df: DataFrame,
    target_column: str,
) -> Div:
    all_subgroups: list[Conjunction] = subgroups_df.subgroup.tolist()
    all_subgroups_str: list[str] = subgroups_df.subgroup_str.tolist()

    @app.callback(
        Output("subgroups-plot", "figure"),
        Input("plot-subgroups-button", "n_clicks"),
        State("subgroups-dropdown", "value"),
    )
    def click_plot_subgroups(
        n_clicks: int, selected_subgroups: list[str]
    ) -> Div | Figure | None:
        # prevents first update, i.e., should only update on the click of the button
        if n_clicks is None:
            raise PreventUpdate

        # if selected subgroups is empty we do nothing on the press of the button
        if len(selected_subgroups) == 0:
            raise PreventUpdate

        selected_subgroup_rows = subgroups_df.query(
            "subgroup_str in @selected_subgroups"
        ).index.tolist()

        first_subgroup = subgroups_df.query(
            f"subgroup_str == '{selected_subgroups[0]}'"
        )[["x_column", "y_column"]]

        columns = first_subgroup.iloc[0].to_dict()

        return plot_graph_and_subgroups(
            dataset_with_errors_df,
            columns["x_column"],
            columns["y_column"],
            subgroups_df.loc[
                selected_subgroup_rows, ["subgroup", "mean_sg", "mean_dataset"]
            ],
            target_column,
        )

    def _filter(subgroup: Conjunction, x_column: str, y_column: str) -> bool:
        x: str = subgroup.selectors[0].attribute_name
        y: str = subgroup.selectors[1].attribute_name
        return (x == x_column and y == y_column) ^ (y == x_column and x == y_column)

    @app.callback(
        Output("subgroups-dropdown", "options"),
        Input("subgroups-dropdown", "value"),
    )
    def filter_subgroups(selected_subgroups: list[str]) -> list[str]:
        if len(selected_subgroups) == 0:
            return all_subgroups_str

        if len(selected_subgroups) > 1:
            raise PreventUpdate

        # get first subgroup cause it is the only one
        first_subgroup = subgroups_df.query(
            f"subgroup_str == '{selected_subgroups[0]}'"
        )[["x_column", "y_column"]]

        # get first line cause it's the only one
        columns = first_subgroup.iloc[0].to_dict()

        subgroups_filtered = filter(
            lambda sg: _filter(sg, columns["x_column"], columns["y_column"]),
            all_subgroups,
        )

        return [str(x) for x in list(subgroups_filtered)]

    return Div(
        className="mt-12 flex items-center place-content-center",
        children=[
            Div(
                className="w-[70%]",
                children=[
                    Dropdown(
                        id="subgroups-dropdown",
                        options=[
                            {
                                "label": rule,
                                "value": rule,
                            }
                            for rule in all_subgroups_str
                        ],
                        value=[],
                        multi=True,
                        placeholder="Selecionar...",
                    ),
                ],
            ),
            Div(
                children=[
                    Button(
                        className="mx-3 text-center uppercase text-[20pt] font-medium p-2 rounded-lg cursor-pointer",
                        children=["Plot"],
                        id="plot-subgroups-button",
                    ),
                ],
            ),
        ],
    )
