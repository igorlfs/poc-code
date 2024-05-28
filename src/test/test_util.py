# ruff: noqa: ANN201
import pytest
from pandas import DataFrame
from pysubgroup import Conjunction, EqualitySelector, IntervalSelector

from src.layout.components.subgroups.util import extract_subgroup_limits

B_LOWER_BOUND = 1.5
B_UPPER_BOUND = 5.5

A_LOWER_BOUND = 2
A_UPPER_BOUND = 3


@pytest.fixture
def df():
    return DataFrame()


@pytest.fixture
def interval_a():
    return IntervalSelector("a", A_LOWER_BOUND, A_UPPER_BOUND)


def test_extract_bounded_subgroups(df: DataFrame, interval_a: IntervalSelector):
    selectors: list[IntervalSelector] = [
        interval_a,
        IntervalSelector("b", B_LOWER_BOUND, B_UPPER_BOUND),
    ]

    subgroup = Conjunction(selectors)

    rule1, rule2, _ = extract_subgroup_limits(subgroup, df)

    assert rule1.lower == A_LOWER_BOUND
    assert rule1.upper == A_UPPER_BOUND

    assert rule2.lower == B_LOWER_BOUND
    assert rule2.upper == B_UPPER_BOUND


def test_extract_equality_selection(df: DataFrame, interval_a: IntervalSelector):
    selectors: list[IntervalSelector | EqualitySelector] = [
        interval_a,
        EqualitySelector("b", B_LOWER_BOUND),
    ]

    subgroup = Conjunction(selectors)

    rule1, rule2, _ = extract_subgroup_limits(subgroup, df)

    assert rule1.lower == A_LOWER_BOUND
    assert rule1.upper == A_UPPER_BOUND

    assert rule2.lower == B_LOWER_BOUND
    assert rule2.upper == B_LOWER_BOUND


def test_too_many_selectors(df: DataFrame, interval_a: IntervalSelector):
    selectors: list[IntervalSelector] = [interval_a, interval_a, interval_a]
    subgroup = Conjunction(selectors)
    with pytest.raises(AssertionError):
        extract_subgroup_limits(subgroup, df)


def test_too_few_selectors(df: DataFrame):
    selectors: list[IntervalSelector] = []
    subgroup = Conjunction(selectors)
    with pytest.raises(AssertionError):
        extract_subgroup_limits(subgroup, df)
