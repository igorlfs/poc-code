import pytest
from pandas import DataFrame
from pysubgroup import Conjunction, EqualitySelector, IntervalSelector

from src.layout.components.subgroups.util import extract_subgroup_limits

B_LOWER_BOUND = 1.5
B_UPPER_BOUND = 5.5

A_LOWER_BOUND = 2
A_UPPER_BOUND = 3


@pytest.fixture
def df() -> DataFrame:
    return DataFrame()


def test_extract_bounded_subgroups(df: DataFrame) -> None:
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


def test_extract_equality_selection(df: DataFrame) -> None:
    selectors: list = [
        EqualitySelector("b", B_LOWER_BOUND),
        IntervalSelector("a", A_LOWER_BOUND, A_UPPER_BOUND),
    ]

    subgroup = Conjunction(selectors)

    rule1, rule2, _ = extract_subgroup_limits(subgroup, df, "", "")

    assert rule1.lower == B_LOWER_BOUND
    assert rule1.upper == B_LOWER_BOUND

    assert rule2.lower == A_LOWER_BOUND
    assert rule2.upper == A_UPPER_BOUND
