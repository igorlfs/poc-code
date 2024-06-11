from dataclasses import dataclass

import pysubgroup as ps
from pandas import DataFrame

NUM_EXPECTED_RULES = 2


@dataclass
class Interval:
    lower: float
    upper: float


message_for_not_implemented_exception = "I can't deal with non numeric features!"


def extract_subgroup_limits(
    subgroup: ps.Conjunction, dataset_df: DataFrame
) -> tuple[Interval, Interval, str]:
    assert len(subgroup.selectors) == NUM_EXPECTED_RULES

    rule1, rule2 = subgroup.selectors

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
    elif isinstance(rule1, ps.EqualitySelector):
        lower = upper = rule1.attribute_value
    else:
        raise NotImplementedError(message_for_not_implemented_exception)

    first = Interval(lower, upper)

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
    elif isinstance(rule2, ps.EqualitySelector):
        lower = upper = rule2.attribute_value
    else:
        raise NotImplementedError(message_for_not_implemented_exception)

    second = Interval(lower, upper)

    return (first, second, rule1.attribute_name)
