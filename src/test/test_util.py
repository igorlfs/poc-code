import pysubgroup as ps
from pandas import DataFrame

from src.layout.components.subgroups.util import extract_subgroup_limits

B_LOWER_BOUND = 1.5
B_UPPER_BOUND = 5.5

A_LOWER_BOUND = 2
A_UPPER_BOUND = 3


def test_extract_bounded_subgroups() -> None:
    df = DataFrame()  # noqa: PD901

    selectors = [
        ps.IntervalSelector("b", B_LOWER_BOUND, B_UPPER_BOUND),
        ps.IntervalSelector("a", A_LOWER_BOUND, A_UPPER_BOUND),
    ]

    subgroup = ps.Conjunction(selectors)

    rule1, rule2 = extract_subgroup_limits(subgroup, df, "", "")

    assert rule1.lower_bound == B_LOWER_BOUND
    assert rule1.upper_bound == B_UPPER_BOUND

    assert rule2.lower_bound == A_LOWER_BOUND
    assert rule2.upper_bound == A_UPPER_BOUND
