from dash import Dash, Input, Output, dcc, html
from dash.html import Div
from pandas import DataFrame
from plotly.graph_objs import Figure

from src.colors import WHITE
from src.layout.components.dendrogram import generate_dendrogram_figure


def threshold(
    app: Dash,
    subgroups_df: DataFrame,
    current_class: str,
) -> Div:
    @app.callback(
        Output("dendrogram-graph", "figure"), Input("slider-position", "value")
    )
    def display_graph(pos_x: float) -> Figure:
        return generate_dendrogram_figure(subgroups_df, current_class, pos_x)

    return Div(
        className="flex justify-center items-center mt-8",
        children=[
            html.H3(
                "Limiar",
                className=f"font-medium rounded-lg text-[{WHITE}]",
            ),
            dcc.Slider(
                id="slider-position",
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
        ],
    )
