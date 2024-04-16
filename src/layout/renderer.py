from dash import Dash, Input, Output, State, dcc, html
from dash.dash import PreventUpdate
from dash.dash_table import DataTable
from pandas import DataFrame
from plotly.graph_objs import Figure

from src.colors import ACCENT, BACKGROUND, CRUST, MANTLE, WHITE
from src.layout.dendogram import generate_dendrogram
from src.layout.sugroups import subgroups


def render_subgroups_table(table_subgroups_df: DataFrame) -> html.Div:
    return html.Div(
        children=[
            DataTable(
                id="rules_table",
                sort_action="native",
                data=table_subgroups_df.to_dict("records"),
                columns=[
                    {
                        "name": c,
                        "id": c,
                        "type": "numeric",
                        "format": {
                            "specifier": ".3f"
                            if c in ("Qualidade", "Erro médio")
                            else ""
                        },
                    }
                    for c in table_subgroups_df.columns
                ],
                style_cell={
                    "textAlign": "center",
                    "overflow": "hidden",
                    "fontFamily": "Ubuntu",
                    "border": "none",
                },
                style_data={
                    "height": "auto",
                    "whiteSpace": "normal",
                    "color": WHITE,
                },
                style_header={
                    "backgroundColor": BACKGROUND,
                    "color": WHITE,
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "textTransform": "uppercase",
                },
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": CRUST},
                    {"if": {"row_index": "even"}, "backgroundColor": MANTLE},
                    {"if": {"column_id": "Tamanho"}, "textAlign": "right"},
                    {"if": {"column_id": "Subgrupo"}, "textAlign": "left"},
                ],
                page_size=20,
                cell_selectable=False,
                style_table={"height": "30%", "overflowY": "auto"},
            ),
        ]
    )


def render_dendogram(subgroups_df: DataFrame) -> html.Div:
    return html.Div(
        className="dendogram-plot",
        children=[
            dcc.Graph(
                id="dendogram-plot",
                figure=generate_dendrogram(subgroups_df),
            ),
        ],
    )


def render_subgroups_dropdown(
    app: Dash, dataset_df: DataFrame, subgroups_df: DataFrame
) -> html.Div:
    all_subgroups: list[str] = subgroups_df.subgroup_str.tolist()

    @app.callback(
        Output("subgroups-plot", "figure"),
        Input("plot-subgroups-button", "n_clicks"),
        State("subgroups-dropdown", "value"),
    )
    def plot_subgroups(
        n_clicks: int, selected_subgroups: list[str]
    ) -> html.Div | Figure:
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

        return subgroups(
            dataset_df=dataset_df,
            x_column=x_column,
            y_column=y_column,
            target=dataset_df.target.tolist(),
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
            "margin-top": "3%",
            "display": "flex",
            "justify-content": "center",
            "align-items": "center",
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
                            "justify-content": "flex-end",
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
