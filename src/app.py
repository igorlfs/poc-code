import pandas as pd
from dash import Dash
from pandas import DataFrame

from src.args import get_args
from src.grouping.clean import remove_redundant_subgroups
from src.grouping.discovery import subgroup_discovery
from src.layout.layout import create_layout


def run() -> None:
    dataset_file_path, errors_file_path, target_column = get_args()
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

    features = dataset_df.columns.tolist()
    features.remove(target_column)
    dataset_with_errors_df = pd.concat([dataset_df, errors_df], axis=1)
    df_list = subgroup_discovery(dataset_df, errors_df, 20, target_column)
    subgroups_df = remove_redundant_subgroups(df_list)

    # Remove subgroups with only group, so we don't have to worry about visualization
    subgroups_df = DataFrame(
        subgroups_df[subgroups_df["subgroup"].apply(lambda x: len(x.selectors) > 1)]
    )

    # adding string column with rules
    subgroups_df["subgroup_str"] = subgroups_df.subgroup.astype(str)

    # adding two extra columns for each coordinate of each rule. If rule contain only one coordinate, second column will be null
    subgroups_df["x_column"] = ""
    subgroups_df["y_column"] = ""

    for idx, subgroup in enumerate(subgroups_df.subgroup):
        rules = subgroup.selectors
        subgroups_df["x_column"].at[idx] = rules[0].attribute_name
        subgroups_df["y_column"].at[idx] = rules[1].attribute_name

    app = Dash(__name__)

    app.title = "Heisenpy"  # TODO temporary name

    # TODO current class should obviously be configurable
    app.layout = create_layout(
        app, dataset_with_errors_df, features, subgroups_df, "setosa", target_column
    )

    app.run(debug=True)
