import pandas as pd
import pysubgroup as ps
from pandas import DataFrame

from src.grouping.lib import BidirectionalQFNumeric


def subgroup_discovery(
    dataset_df: DataFrame,
    errors_df: DataFrame,
    set_size: int,
    target_column: str,
    current_class: str,
) -> DataFrame:
    merged_df = pd.concat([dataset_df.drop(target_column, axis=1), errors_df], axis=1)
    search_space = ps.create_selectors(merged_df, ignore=errors_df.columns.to_list())
    task = ps.SubgroupDiscoveryTask(
        data=merged_df,
        target=ps.NumericTarget(current_class),
        search_space=search_space,
        result_set_size=set_size,
        depth=2,
        qf=BidirectionalQFNumeric(a=0.5),
    )
    df_rules = ps.BeamSearch(beam_width=set_size).execute(task=task).to_dataframe()
    df_rules["covered"] = df_rules["subgroup"].apply(lambda x: x.covers(merged_df))
    return df_rules
