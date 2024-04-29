from dash import Dash, dcc, html
from pandas import DataFrame

from src.layout.components.dendogram import generate_dendrogram_figure
from src.layout.components.dropdown import subgroups_dropdown
from src.layout.components.graph import plot_graph_and_subgroups
from src.layout.components.table import data_table


def create_layout(
    app: Dash,
    dataset_with_errors_df: DataFrame,
    features: list[str],
    subgroups_df: DataFrame,
    current_class: str,
    target_column: str,
) -> html.Div:
    table_subgroups_df = DataFrame(
        subgroups_df.query(f"`class` == '{current_class}'")[
            ["subgroup_str", "size_sg", "mean_sg", "quality"]
        ]
    ).rename(
        columns={
            "subgroup_str": "Subgrupo",
            "size_sg": "Tamanho",
            "mean_sg": "Erro médio",
            "quality": "Qualidade",
        }
    )

    x_column = features[0]
    y_column = features[1]

    return html.Div(
        id="main-layout",
        style={
            "display": "flex-col",
        },
        children=[
            html.Div(
                children=[
                    html.H1(
                        "Heisenpy",
                    ),
                    html.Div(
                        style={
                            "display": "flex",
                            "justifyContent": "flex-auto",
                            "placeContent": "space-evenly",
                        },
                        children=[
                            html.Div(
                                className="subgroups-datatable",
                                style={
                                    "display": "flex",
                                    "justifyContent": "center",
                                    "alignItems": "center",
                                },
                                children=[data_table(table_subgroups_df)],
                            ),
                            html.Div(
                                style={
                                    "display": "flex",
                                    "justifyContent": "center",
                                    "alignItems": "center",
                                },
                                children=[
                                    dcc.Graph(
                                        id="dendogram-plot",
                                        figure=generate_dendrogram_figure(
                                            subgroups_df, current_class
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    subgroups_dropdown(
                        app,
                        dataset_with_errors_df,
                        subgroups_df.query(f"`class` == '{current_class}'"),
                        target_column,
                    ),
                    plot_graph_and_subgroups(
                        dataset_with_errors_df,
                        x_column,
                        y_column,
                        None,
                        target_column,
                    ),
                ],
            ),
        ],
    )
