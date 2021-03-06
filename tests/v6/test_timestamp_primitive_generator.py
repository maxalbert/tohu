import datetime as dt
import pytest

from .context import tohu
from tohu.v6.primitive_generators import Timestamp, TohuTimestampError


@pytest.mark.parametrize(
    "start, end, date, start_expected, end_expected",
    [
        (
            "2018-01-01 11:22:33",
            "2018-06-28 22:11:02",
            None,
            dt.datetime(2018, 1, 1, 11, 22, 33),
            dt.datetime(2018, 6, 28, 22, 11, 2),
        ),
        (
            "2018-01-01 11:22:33",
            None,
            "2018-01-01",
            dt.datetime(2018, 1, 1, 11, 22, 33),
            dt.datetime(2018, 1, 1, 23, 59, 59),
        ),
        (
            None,
            "2018-01-01 11:12:13",
            "2018-01-01",
            dt.datetime(2018, 1, 1, 0, 0, 0),
            dt.datetime(2018, 1, 1, 11, 12, 13),
        ),
        (
            None,
            None,
            "2018-05-09",
            dt.datetime(2018, 5, 9, 0, 0, 0),
            dt.datetime(2018, 5, 9, 23, 59, 59),
        ),
        (
            "2018-01-01 04:05:06",
            "2018-01-01 11:22:33",
            None,
            dt.datetime(2018, 1, 1, 4, 5, 6),
            dt.datetime(2018, 1, 1, 11, 22, 33),
        ),
        (
            "2018-01-01 04:05:06",
            "2018-01-01 04:05:06",
            None,
            dt.datetime(2018, 1, 1, 4, 5, 6),
            dt.datetime(2018, 1, 1, 4, 5, 6),
        ),
    ],
)
def test_expected_start_and_end_value(start, end, date, start_expected, end_expected):
    g = Timestamp(start=start, end=end, date=date)

    assert start_expected == g.start
    assert end_expected == g.end


@pytest.mark.parametrize(
    "start, end, date",
    [
        (None, None, None),  # at least one if the arguments must be provided
        (
            None,
            "2018-01-01 11:22:33",
            None,
        ),  # date must be given if start timestamp is omitted
        (
            "2018-01-01 11:22:33",
            None,
            None,
        ),  # date must be given if end timestamp is omitted
        (
            "2018-06-14 11:12:13",
            None,
            "2018-05-09",
        ),  # date of start timestamp does not coincide with date argument
        (
            None,
            "2018-06-14 11:12:13",
            "2018-05-09",
        ),  # date of end timestamp does not coincide with date argument
        (
            "2018-01-01 04:05:06",
            "2018-01-01 11:12:13",
            "2018-01-01",
        ),  # not all arguments must be provided
        (
            "2018-01-01 11:22:33",
            "2018-01-01 04:05:06",
            None,
        ),  # start timestamp must not be after end timestamp
    ],
)
def test_invalid_input_combinations(start, end, date):
    with pytest.raises(TohuTimestampError):
        Timestamp(start=start, end=end, date=date)
