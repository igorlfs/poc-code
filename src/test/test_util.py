from pandas import DataFrame
from pysubgroup import Conjunction, IntervalSelector

from src.layout.components.subgroups.util import extract_subgroup_limits

B_LOWER_BOUND = 1.5
B_UPPER_BOUND = 5.5

A_LOWER_BOUND = 2
A_UPPER_BOUND = 3


def test_extract_bounded_subgroups() -> None:
    df = DataFrame()

    selectors: list[IntervalSelector] = [
        IntervalSelector("b", B_LOWER_BOUND, B_UPPER_BOUND),
        IntervalSelector("a", A_LOWER_BOUND, A_UPPER_BOUND),
    ]

    subgroup = Conjunction(selectors)

    rule1, rule2, _ = extract_subgroup_limits(subgroup, df, "", "")

    assert rule1.lower == B_LOWER_BOUND
    assert rule1.upper == B_UPPER_BOUND

    assert rule2.lower == A_LOWER_BOUND
    assert rule2.upper == A_UPPER_BOUND
