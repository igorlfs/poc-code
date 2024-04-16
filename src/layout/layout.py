from dash import Dash, html
from pandas import DataFrame

from src.layout.renderer import (
    render_dendogram,
    render_subgroups_dropdown,
    render_subgroups_table,
)
from src.layout.sugroups import subgroups


def create_layout(
    app: Dash, dataset_df: DataFrame, subgroups_df: DataFrame, class_of_interest: int
) -> html.Div:
    table_subgroups_df = DataFrame(
        subgroups_df.query(f"`class` == {class_of_interest}")[
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
                            "justify-content": "flex-auto",
                            "place-content": "space-evenly",
                        },
                        children=[
                            html.Div(
                                className="subgroups-datatable",
                                style={
                                    "display": "flex",
                                    "justify-content": "center",
                                    "align-items": "center",
                                },
                                children=[render_subgroups_table(table_subgroups_df)],
                            ),
                            html.Div(
                                className="dendogram-plot",
                                style={
                                    "display": "flex",
                                    "justify-content": "center",
                                    "align-items": "center",
                                },
                                children=[render_dendogram(subgroups_df)],
                            ),
                        ],
                    ),
                    render_subgroups_dropdown(
                        app=app,
                        dataset_df=dataset_df,
                        subgroups_df=subgroups_df.query(
                            f"`class` == {class_of_interest}"
                        ),
                    ),
                    subgroups(
                        dataset_df=dataset_df,
                        x_column="petal width (cm)",
                        y_column="petal length (cm)",
                        target=dataset_df.target.tolist(),
                        subgroups=None,
                    ),
                ],
            ),
        ],
    )
