from dash.dash_table import DataTable
from pandas import DataFrame

from src.colors import BACKGROUND, CRUST, MANTLE, WHITE


def data_table(subgroups_df: DataFrame) -> DataTable:
    table_subgroups_df = DataFrame(
        subgroups_df[["subgroup", "size_sg", "mean_sg", "quality"]]
    ).rename(
        columns={
            "subgroup": "Subgroup",
            "size_sg": "Size",
            "mean_sg": "Avg Error",
            "quality": "Quality",
        }
    )
    table_subgroups_df["Subgroup"] = table_subgroups_df["Subgroup"].astype(str)

    return DataTable(
        id="rules_table",
        sort_action="native",
        data=table_subgroups_df.to_dict("records"),
        columns=[
            {
                "name": c,
                "id": c,
                "type": "numeric",
                "format": {"specifier": ".3f" if c in ("Quality", "Avg Error") else ""},
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
            "paddingLeft": "10px",
            "paddingRight": "10px",
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
            {"if": {"column_id": "Quality"}, "textAlign": "right"},
            {"if": {"column_id": "Size"}, "textAlign": "right"},
            {"if": {"column_id": "Subgroup"}, "textAlign": "left"},
        ],
        cell_selectable=False,
        style_table={"height": "600px", "overflowY": "auto"},
    )
