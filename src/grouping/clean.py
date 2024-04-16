from typing import Hashable

import pandas as pd
from pandas import DataFrame
from tqdm import tqdm


# Reducing the redundancy in the subgroups mined, by unifying the names of equal coverage subgroup descriptions
def remove_redundant_subgroups(df_list: list[DataFrame]) -> DataFrame:
    df_rules = pd.concat(df_list, ignore_index=True)
    list_of_rules: list[dict] = []

    # First, we create a list of the subgroup descriptions and its coverage sets
    for _, rule_row in tqdm(df_rules.iterrows()):
        percent_equals = 0

        row_subgroup = rule_row["subgroup"]
        row_covered = rule_row["covered"]

        # variable must be Hashable to create a set
        assert isinstance(row_subgroup, Hashable)

        for rule in list_of_rules:
            percent_equals = sum(row_covered & rule["covered"]) / sum(
                row_covered | rule["covered"]
            )
            if percent_equals == 1:
                rule["subgroup"].add(row_subgroup)
                break
        if percent_equals != 1:
            list_of_rules.append({"subgroup": {row_subgroup}, "covered": row_covered})

    # Then, we create a dictionary to replace all descriptions by the first of them
    duplicate_rules = [x["subgroup"] for x in list_of_rules if len(x["subgroup"]) > 1]
    rule_map = {}
    for duplicate in duplicate_rules:
        first_rule = None
        for rule in duplicate:
            if first_rule is None:
                first_rule = rule
            else:
                rule_map[rule] = first_rule

    return df_rules.replace({"subgroup": rule_map})
