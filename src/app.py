import pandas as pd
from dash import Dash
from pandas import DataFrame

from src.args import get_args
from src.grouping.clean import remove_redundant_subgroups
from src.grouping.discovery import subgroup_discovery
from src.layout.layout import create_layout


def get_dfs(dataset_path: str, errors_path: str) -> None | tuple[DataFrame, DataFrame]:
    try:
        dataset_df = pd.read_csv(dataset_path)
        errors_df = pd.read_csv(errors_path)
    except FileNotFoundError as e:
        print(f"File '{e}' not found")
        return None
    except pd.errors.ParserError:
        print("Error parsing input files. Make sure they are CSVs")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

    return (dataset_df, errors_df)


def run() -> None:
    dataset_file_path, errors_file_path, target_column, current_class, size = get_args()
    dfs = get_dfs(dataset_file_path, errors_file_path)
    if dfs is None:
        return
    dataset_df, errors_df = dfs

    if target_column not in dataset_df.columns:
        print(f"Missing target column '{target_column}' in dataset")
        return

    if current_class not in errors_df.columns:
        print(f"Missing current column '{current_class}' in errors dataframe")
        return

    if current_class not in dataset_df[target_column].unique():
        print(f"Current class '{current_class}' doesn't appear in dataset")
        return

    features = dataset_df.columns.tolist()
    features.remove(target_column)
    dataset_with_errors_df = pd.concat([dataset_df, errors_df], axis=1)
    subgroups_df = subgroup_discovery(
        dataset_df, errors_df, size, target_column, current_class
    )
    subgroups_df = remove_redundant_subgroups(subgroups_df)

    # Remove subgroups with only group, so we don't have to worry about visualization
    subgroups_df = subgroups_df[
        subgroups_df["subgroup"].apply(lambda x: len(x.selectors) > 1)
    ]

    subgroups_df = subgroups_df.reset_index(drop=True)

    if subgroups_df.empty:
        print("No subgroups have been found")
        return

    # adding columns for axis of each rule
    subgroups_df["x_column"] = subgroups_df["subgroup"].apply(
        lambda x: x.selectors[0].attribute_name
    )
    subgroups_df["y_column"] = subgroups_df["subgroup"].apply(
        lambda x: x.selectors[1].attribute_name
    )

    app = Dash(
        __name__,
        external_scripts=[{"src": "https://cdn.tailwindcss.com"}],
    )

    app.title = "Heisenpy"  # TODO temporary name

    app.layout = create_layout(
        dataset_with_errors_df,
        features,
        subgroups_df,
        target_column,
        current_class,
    )

    app.run()
