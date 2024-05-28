from dash.dash_table import DataTable
from pandas import DataFrame

from src.colors import BACKGROUND, CRUST, MANTLE, WHITE


def data_table(subgroups_df: DataFrame, current_class: str) -> DataTable:
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

    return DataTable(
        id="rules_table",
        sort_action="native",
        data=table_subgroups_df.to_dict("records"),
        columns=[
            {
                "name": c,
                "id": c,
                "type": "numeric",
                "format": {
                    "specifier": ".3f" if c in ("Qualidade", "Erro médio") else ""
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
    )
