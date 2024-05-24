from dataclasses import dataclass

import pysubgroup as ps
from pandas import DataFrame


@dataclass
class Interval:
    lower: float
    upper: float


message_for_not_implemented_exception = "I still can't deal with non numeric features!"


def extract_subgroup_limits(
    subgroup: ps.Conjunction, dataset_df: DataFrame, x_column: str, y_column: str
) -> tuple[Interval, Interval, str]:
    rule1, _ = subgroup.selectors

    if isinstance(rule1, ps.IntervalSelector):
        lower = (
            dataset_df[rule1.attribute_name].min()
            if rule1.lower_bound == float("-inf")
            else rule1.lower_bound
        )
        upper = (
            dataset_df[rule1.attribute_name].max()
            if rule1.upper_bound == float("inf")
            else rule1.upper_bound
        )
        first = Interval(lower, upper)
    else:
        raise NotImplementedError(message_for_not_implemented_exception)

    if len(subgroup.selectors) < 2:  # noqa: PLR2004
        rule2_attribute = y_column if rule1.attribute_name == x_column else x_column
        lower = dataset_df[rule2_attribute].min()
        upper = dataset_df[rule2_attribute].max()
    else:
        rule2 = subgroup.selectors[1]
        if isinstance(rule2, ps.IntervalSelector):
            lower = (
                dataset_df[rule2.attribute_name].min()
                if rule2.lower_bound == float("-inf")
                else rule2.lower_bound
            )
            upper = (
                dataset_df[rule2.attribute_name].max()
                if rule2.upper_bound == float("inf")
                else rule2.upper_bound
            )
        else:
            raise NotImplementedError(message_for_not_implemented_exception)

    second = Interval(lower, upper)

    return (first, second, rule1.attribute_name)
