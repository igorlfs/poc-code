from pandas import DataFrame


# Reducing the redundancy in the subgroups mined, by unifying the names of equal coverage subgroup descriptions
def remove_redundant_subgroups(subgroups_df: DataFrame) -> DataFrame:
    list_of_rules: list[dict] = []

    # First, we create a list of the subgroup descriptions and its coverage sets
    for _, rule_row in subgroups_df.iterrows():
        percent_equals = 0

        row_subgroup = rule_row["subgroup"]
        row_covered = rule_row["covered"]

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

    return subgroups_df.replace({"subgroup": rule_map}).drop_duplicates(
        subset="subgroup"
    )
