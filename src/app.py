import pandas as pd
from dash import Dash
from pandas import DataFrame

from src.args import get_args
from src.grouping.clean import remove_redundant_subgroups
from src.grouping.discovery import subgroup_discovery
from src.layout.layout import create_layout


def run() -> None:
    dataset_file_path, errors_file_path = get_args()
    dataset_df: DataFrame
    errors_df: DataFrame

    try:
        dataset_df = pd.read_csv(dataset_file_path)
        errors_df = pd.read_csv(errors_file_path)
    except FileNotFoundError as e:
        print(f"File '{e}' not found")
        return
    except pd.errors.ParserError:
        print("Error parsing input files. Make sure they are CSVs")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

    # subgroup discovery doesn't work if the names are strings
    errors_df.columns = list(range(len(errors_df.columns)))

    df_list = subgroup_discovery(dataset_df, errors_df, 3)
    subgroups_df = remove_redundant_subgroups(df_list)

    # adding string column with rules
    subgroups_df["subgroup_str"] = subgroups_df.subgroup.astype(str)

    # adding two extra columns for each coordinate of each rule. If rule contain only one coordinate, second column will be null
    subgroups_df["x_column"] = ""
    subgroups_df["y_column"] = ""

    for idx, subgroup in enumerate(subgroups_df.subgroup):
        rules = subgroup.selectors
        if len(rules) < 2:  # noqa: PLR2004
            subgroups_df["x_column"].at[idx] = rules[0].attribute_name
        else:
            subgroups_df["x_column"].at[idx] = rules[0].attribute_name
            subgroups_df["y_column"].at[idx] = rules[1].attribute_name

    app = Dash(__name__, assets_folder="./assets/")

    app.title = "Heisenpy"  # TODO temporary name

    app.layout = create_layout(app, dataset_df, subgroups_df, 0)

    app.run(debug=True)
