import pandas as pd
import pysubgroup as ps
from pandas import DataFrame

from src.grouping.lib import BidirectionalQFNumeric


def subgroup_discovery(
    dataset_df: DataFrame, errors_df: DataFrame, number_of_classes: int
) -> list[DataFrame]:
    dataset_clone_df = dataset_df.drop("target", axis=1)

    df_rules_list: list[DataFrame] = []

    data = pd.concat([dataset_clone_df, errors_df], axis=1)
    for class_of_interest in range(number_of_classes):
        target = ps.NumericTarget(class_of_interest)
        search_space = ps.create_selectors(data, ignore=range(number_of_classes))
        task = ps.SubgroupDiscoveryTask(
            data,
            target,
            search_space,
            result_set_size=20,
            depth=2,
            qf=BidirectionalQFNumeric(a=0.5),
        )
        df_rules = ps.BeamSearch().execute(task=task).to_dataframe()

        df_rules["covered"] = df_rules["subgroup"].apply(lambda x: x.covers(data))
        df_rules["class"] = class_of_interest

        df_rules_list.append(df_rules.copy())

    return df_rules_list
