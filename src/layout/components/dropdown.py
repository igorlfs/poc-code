from dash import Input, Output, State, callback
from dash.dash import PreventUpdate
from dash.dcc import Dropdown
from dash.html import Button, Div
from pandas import DataFrame
from plotly.graph_objs import Figure

from src.layout.components.graph import plot_graph_and_subgroups


def subgroups_dropdown(
    dataset_with_errors_df: DataFrame,
    subgroups_df: DataFrame,
    target_column: str,
) -> Div:
    @callback(
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

        selected_subgroup_rows = subgroups_df["subgroup"].apply(
            lambda x: str(x) in selected_subgroups
        )

        first_subgroup_filter = subgroups_df["subgroup"].apply(
            lambda x: str(x) == selected_subgroups[0]
        )
        first_subgroup = subgroups_df.loc[first_subgroup_filter]

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

    return Div(
        className="mt-6 flex items-center place-content-center",
        children=[
            Div(
                className="w-[70%]",
                children=[
                    Dropdown(
                        id="subgroups-dropdown",
                        value=[],
                        multi=True,
                    ),
                ],
            ),
            Div(
                children=[
                    Button(
                        className="mx-3 text-center text-[20pt] font-bold p-2 rounded-lg cursor-pointer uppercase",
                        children=["Plot"],
                        id="plot-subgroups-button",
                    ),
                ],
            ),
        ],
    )
