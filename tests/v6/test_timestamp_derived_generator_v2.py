import datetime as dt
import pytest

from operator import attrgetter

from .context import tohu
from tohu.v6.primitive_generators import Constant
from tohu.v6.derived_generators_v2 import TimestampDerived, TohuTimestampError


@pytest.mark.parametrize(
    "start, end, date, start_attr, end_attr, start_expected, end_expected",
    [
        (
            "2018-01-01 11:22:33",
            "2018-06-28 22:11:02",
            None,
            "start_gen.value",
            "end_gen.value",
            dt.datetime(2018, 1, 1, 11, 22, 33),
            dt.datetime(2018, 6, 28, 22, 11, 2),
        ),
        (
            "2018-01-01 11:22:33",
            None,
            "2018-01-01",
            "start_gen.value",
            "end_gen.value",
            dt.datetime(2018, 1, 1, 11, 22, 33),
            dt.datetime(2018, 1, 1, 23, 59, 59),
        ),
        (
            None,
            "2018-01-01 11:12:13",
            "2018-01-01",
            "start_gen.value",
            "end_gen.value",
            dt.datetime(2018, 1, 1, 0, 0, 0),
            dt.datetime(2018, 1, 1, 11, 12, 13),
        ),
        (
            None,
            None,
            "2018-05-09",
            "start_gen.value",
            "end_gen.value",
            dt.datetime(2018, 5, 9, 0, 0, 0),
            dt.datetime(2018, 5, 9, 23, 59, 59),
        ),
        (
            "2018-01-01 04:05:06",
            "2018-01-01 11:22:33",
            None,
            "start_gen.value",
            "end_gen.value",
            dt.datetime(2018, 1, 1, 4, 5, 6),
            dt.datetime(2018, 1, 1, 11, 22, 33),
        ),
        (
            "2018-01-01 04:05:06",
            "2018-01-01 04:05:06",
            None,
            "start_gen.value",
            "end_gen.value",
            dt.datetime(2018, 1, 1, 4, 5, 6),
            dt.datetime(2018, 1, 1, 4, 5, 6),
        ),
    ],
)
def test_expected_start_and_end_value_with_string_inputs(start, end, date, start_attr, end_attr, start_expected, end_expected):
    g = TimestampDerived(start=start, end=end, date=date)

    assert start_expected == attrgetter(start_attr)(g)
    assert end_expected == attrgetter(end_attr)(g)


@pytest.mark.parametrize(
    "start, end, date, start_attr, end_attr, start_expected, end_expected",
    [
        (
            Constant("2018-01-01 11:22:33"),
            Constant("2018-06-28 22:11:02"),
            None,
            "start_gen.value",
            "end_gen.value",
            dt.datetime(2018, 1, 1, 11, 22, 33),
            dt.datetime(2018, 6, 28, 22, 11, 2),
        ),
        (
            Constant("2018-01-01 11:22:33"),
            None,
            Constant("2018-01-01"),
            "start_gen.value",
            "end_gen.value",
            dt.datetime(2018, 1, 1, 11, 22, 33),
            dt.datetime(2018, 1, 1, 23, 59, 59),
        ),
        (
            None,
            Constant("2018-01-01 11:12:13"),
            Constant("2018-01-01"),
            "start_gen.value",
            "end_gen.value",
            dt.datetime(2018, 1, 1, 0, 0, 0),
            dt.datetime(2018, 1, 1, 11, 12, 13),
        ),
        (
            None,
            None,
            Constant("2018-05-09"),
            "start_gen.value",
            "end_gen.value",
            dt.datetime(2018, 5, 9, 0, 0, 0),
            dt.datetime(2018, 5, 9, 23, 59, 59),
        ),
    ],
)
def test_expected_start_and_end_value_with_constant_inputs(start, end, date, start_attr, end_attr, start_expected, end_expected):
    g = TimestampDerived(start=start, end=end, date=date)

    assert start_expected == attrgetter(start_attr)(g)
    assert end_expected == attrgetter(end_attr)(g)
