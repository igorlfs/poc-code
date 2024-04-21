from dash import Dash, Input, Output, State, dcc, html
from dash.dash import PreventUpdate
from pandas import DataFrame
from plotly.graph_objs import Figure

from src.colors import ACCENT, CRUST, WHITE
from src.layout.subgroups import plot_graph_and_subgroups


def subgroups_dropdown(
    app: Dash, dataset_with_errors_df: DataFrame, subgroups_df: DataFrame
) -> html.Div:
    all_subgroups: list[str] = subgroups_df.subgroup_str.tolist()

    @app.callback(
        Output("subgroups-plot", "figure"),
        Input("plot-subgroups-button", "n_clicks"),
        State("subgroups-dropdown", "value"),
    )
    def click_plot_subgroups(
        n_clicks: int, selected_subgroups: list[str]
    ) -> html.Div | Figure | None:
        # prevents first update, i.e., should only update on the click of the button
        if n_clicks is None:
            raise PreventUpdate

        # if selected subgroups is empty we do nothing on the press of the button
        if len(selected_subgroups) == 0:
            raise PreventUpdate

        df_rows: list[int] = []
        df_rows = [
            subgroups_df.index[subgroups_df.subgroup_str == subgroup].tolist()[0]
            for subgroup in selected_subgroups
        ]

        # we assume the selected subgroup is of size 2, and we arbitrarily use the first one as x_axis and second one as y_axis of 2d plot

        first_subgroup = subgroups_df[
            subgroups_df["subgroup_str"] == selected_subgroups[0]
        ]

        x_column = first_subgroup.x_column.iloc[0]
        y_column = first_subgroup.y_column.iloc[0]

        # TODO handle single feature
        return plot_graph_and_subgroups(
            dataset_with_errors_df,
            x_column=x_column,
            y_column=y_column,
            subgroups=subgroups_df.loc[
                df_rows, ["subgroup", "mean_sg", "mean_dataset"]
            ],
        )

    @app.callback(
        Output("subgroups-dropdown", "options"),
        Input("subgroups-dropdown", "value"),
    )
    def filter_subgroups(selected_subgroups: list[str]) -> list[str]:
        if len(selected_subgroups) == 0:
            return all_subgroups

        if len(selected_subgroups) > 1:
            raise PreventUpdate

        # get first cause it is the only one
        first_subgroup = subgroups_df[
            subgroups_df["subgroup_str"] == selected_subgroups[0]
        ]

        # case where only one dimension defines rule
        if first_subgroup.y_column.iloc[0] == "":
            return subgroups_df[
                (subgroups_df.x_column == first_subgroup.x_column.iloc[0])
                ^ (subgroups_df.y_column == first_subgroup.x_column.iloc[0])
            ].subgroup_str.tolist()

        return subgroups_df[
            (
                (subgroups_df.x_column == first_subgroup.x_column.iloc[0])
                & (subgroups_df.y_column == first_subgroup.y_column.iloc[0])
            )
            ^ (
                (subgroups_df.x_column == first_subgroup.y_column.iloc[0])
                & (subgroups_df.y_column == first_subgroup.x_column.iloc[0])
            )
        ].subgroup_str.tolist()

    return html.Div(
        id="subgroups-container",
        style={
            "marginTop": "3%",
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
        },
        children=[
            html.Div(
                className="subgroups-search",
                style={
                    "display": "flex-row",
                    "width": "80%",
                },
                children=[
                    dcc.Dropdown(
                        id="subgroups-dropdown",
                        options=[
                            {
                                "label": rule,
                                "value": rule,
                            }
                            for rule in all_subgroups
                        ],
                        value=[],
                        multi=True,
                        placeholder="Selecionar...",
                        style={
                            "border": "none",
                        },
                    ),
                    html.Div(
                        style={
                            "display": "flex",
                            "justifyContent": "flex-end",
                        },
                        children=[
                            html.Button(
                                className="dropdown-button",
                                children=["Plot"],
                                id="plot-subgroups-button",
                                style={
                                    "marginTop": "1%",
                                    "textAlign": "center",
                                    "display": "inline-block",
                                    "backgroundColor": ACCENT,
                                    "fontSize": "20pt",
                                    "fontFamily": "Ubuntu",
                                    "fontWeight": "500",
                                    "color": CRUST,
                                    "textTransform": "uppercase",
                                    "padding": "10px",
                                    "borderRadius": "8px",
                                    "border": "none",
                                    "cursor": "pointer",
                                },
                            ),
                        ],
                    ),
                ],
            )
        ],
    )


def columns_dropdown(features: list[str], x_column: str, y_column: str) -> html.Div:
    # TODO filter columns so they have to be different
    return html.Div(
        style={
            "marginTop": "2%",
            "marginBottom": "1%",
            "display": "flex",
            "placeContent": "space-evenly",
        },
        children=[
            dcc.Dropdown(
                id="xaxes-dropdown",
                style={
                    "width": "600px",
                    "color": WHITE,
                },
                value=x_column,
                options=[
                    {
                        "label": rule,
                        "value": rule,
                    }
                    for rule in features
                ],
            ),
            dcc.Dropdown(
                id="yaxes-dropdown",
                value=y_column,
                style={
                    "width": "600px",
                    "color": WHITE,
                },
                options=[
                    {
                        "label": rule,
                        "value": rule,
                    }
                    for rule in features
                ],
            ),
        ],
    )
