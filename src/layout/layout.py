from dash import Dash
from dash.dcc import Graph
from dash.html import Div
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
) -> Div:
    return Div(
        className="flex-col mt-12",
        children=[
            Div(
                children=[
                    Div(
                        className="flex xl:flex-row xl:place-content-evenly flex-col",
                        children=[
                            Div(
                                className="flex justify-center items-center",
                                children=[data_table(subgroups_df, current_class)],
                            ),
                            Div(
                                className="flex justify-center mt-10 xl:mt-0",
                                children=[
                                    Graph(
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
                        features[0],
                        features[1],
                        None,
                        target_column,
                    ),
                ],
            ),
        ],
    )
