import pysubgroup as ps
from pandas import DataFrame

message_for_not_implemented_exception = "I still can't deal with non numeric features!"


def extract_subgroup_limits(
    subgroup: ps.Conjunction, dataset_df: DataFrame, x_column: str, y_column: str
) -> tuple[ps.IntervalSelector, ps.IntervalSelector]:
    rule1, _ = subgroup.selectors

    if isinstance(rule1, ps.IntervalSelector):
        if rule1.lower_bound == float("-inf"):
            rule1._lower_bound = dataset_df[rule1.attribute_name].min()
        if rule1.upper_bound == float("inf"):
            rule1._upper_bound = dataset_df[rule1.attribute_name].max()
    else:
        raise NotImplementedError(message_for_not_implemented_exception)

    if len(subgroup.selectors) < 2:  # noqa: PLR2004
        rule2_attribute = y_column if rule1.attribute_name == x_column else x_column
        rule2 = ps.IntervalSelector(
            rule2_attribute,
            dataset_df[rule2_attribute].min(),
            dataset_df[rule2_attribute].max(),
        )
    else:
        rule2 = subgroup.selectors[1]
        if isinstance(rule2, ps.IntervalSelector):
            if rule2.lower_bound == float("-inf"):
                rule2._lower_bound = dataset_df[rule2.attribute_name].min()
            if rule2.upper_bound == float("inf"):
                rule2._upper_bound = dataset_df[rule2.attribute_name].max()
        else:
            raise NotImplementedError(message_for_not_implemented_exception)

    return rule1, rule2
