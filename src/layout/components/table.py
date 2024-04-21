from dash.dash_table import DataTable
from pandas import DataFrame

from src.colors import BACKGROUND, CRUST, MANTLE, WHITE


def data_table(table_subgroups_df: DataFrame) -> DataTable:
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
