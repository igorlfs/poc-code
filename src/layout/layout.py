from dash import html
from dash.dcc import Graph
from dash.html import Div
from pandas import DataFrame

from src.layout.components.dendrogram import generate_dendrogram_figure
from src.layout.components.dropdown import subgroups_dropdown
from src.layout.components.graph import plot_graph_and_subgroups
from src.layout.components.table import data_table
from src.layout.components.threshold import threshold


def create_layout(
    dataset_with_errors_df: DataFrame,
    features: list[str],
    subgroups_df: DataFrame,
    target_column: str,
    current_class: str,
) -> Div:
    dendrogram, min_x, max_x = generate_dendrogram_figure(subgroups_df, None)
    return Div(
        className="flex-col mt-6",
        children=[
            Div(
                children=[
                    html.H2(
                        f"Uncertainty Regions for {current_class}",
                        className="text-center mb-6",
                    ),
                    Div(
                        className="flex xl:flex-row-reverse xl:place-content-evenly flex-col",
                        children=[
                            Div(
                                className="flex justify-center items-center",
                                children=[data_table(subgroups_df)],
                            ),
                            Div(
                                className="flex flex-col items-center mt-10 xl:mt-0",
                                children=[
                                    Graph(
                                        id="dendrogram-graph",
                                        figure=dendrogram,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    threshold(subgroups_df, min_x, max_x),
                    subgroups_dropdown(
                        dataset_with_errors_df,
                        subgroups_df,
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
