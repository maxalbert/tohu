import datetime as dt
import pytest

from operator import attrgetter

from .context import tohu
from tohu.v6.primitive_generators import Timestamp as TimestampPrimitive
from tohu.v6.derived_generators import TohuTimestampError, Timestamp as TimestampDerived


def test_initialising_with_string_and_timestamp_yields_same_results():
    t_start = dt.datetime(2018, 1, 1, 11, 22, 33)
    t_end = dt.datetime(2018, 1, 1, 12, 23, 34)

    g1 = TimestampDerived(start="2018-01-01 11:22:33", end="2018-01-01 12:23:34")
    g2 = TimestampDerived(start=t_start, end=t_end)
    timestamps_1 = g1.generate(100, seed=12345)
    timestamps_2 = g2.generate(100, seed=12345)

    assert all([(x == y) for x, y in zip(timestamps_1, timestamps_2)])


def test_generated_timestamps_are_between_start_and_end_values():
    t_start = dt.datetime(2018, 1, 1, 11, 22, 33)
    t_end = dt.datetime(2018, 1, 1, 12, 23, 34)

    g = TimestampDerived(start=t_start, end=t_end)
    timestamps = g.generate(100, seed=12345)
    assert all([(t_start <= x <= t_end) for x in timestamps])


@pytest.mark.xfail(reason="Dates as arguments for start/end are not currently supported")
def test_can_pass_dates_for_start_and_end():
    """
    If a date of the form "YYYY-MM-DD" is passed for `start` instead of a
    full timestamp, it is interpreted as "YYYY-MM-DD 00:00:00". Similarly,
    if a date is passed for `end` it is interpreted as "YYYY-MM-DD 23:59:59".
    """
    # g1 and g2 should produce the same timestamps
    g1 = TimestampDerived(start="2018-04-29", end="2018-04-29")
    g2 = TimestampDerived(start="2018-04-29 00:00:00", end="2018-04-29 23:59:59")

    # g3 and g4 should produce different timestamps than g1 and g2
    g3 = TimestampDerived(start="2018-04-29 00:00:01", end="2018-04-29 23:59:59")
    g4 = Timestamp(start="2018-04-29 00:00:00", end="2018-04-29 23:59:58")

    timestamps_1 = g1.generate(10000, seed=12345)
    timestamps_2 = g2.generate(10000, seed=12345)
    timestamps_3 = g3.generate(10000, seed=12345)
    timestamps_4 = g3.generate(10000, seed=12345)

    assert all([(x == y) for x, y in zip(timestamps_1, timestamps_2)])
    assert not all([(x == y) for x, y in zip(timestamps_1, timestamps_3)])
    assert not all([(x == y) for x, y in zip(timestamps_1, timestamps_4)])


def test_start_can_be_equal_to_end():
    g = TimestampDerived(start="2018-01-01 11:22:33", end="2018-01-01 11:22:33")
    timestamps = g.generate(10, seed=12345)
    assert all([x == dt.datetime(2018, 1, 1, 11, 22, 33) for x in timestamps])


def test_raises_error_if_start_is_later_than_end():
    with pytest.raises(TohuTimestampError, match="Start value must be before end value"):
        TimestampDerived(start="2018-01-01 11:22:33", end="2018-01-01 10:09:08")


def test_raises_error_if_start_generator_produces_timestamps_later_than_end_generator():
    g_start = TimestampPrimitive(start="2018-01-01 00:00:00", end="2018-01-30 23:59:59")
    g_end = TimestampPrimitive(start="2018-01-02 00:00:00", end="2018-01-31 23:59:59")

    with pytest.raises(TohuTimestampError, match="Latest possible value of 'start' generator must not be after earliest possible value of 'end' generator"):
        TimestampDerived(start=g_start, end=g_end)


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
    ],
)
def test_expected_start_and_end_value(start, end, date, start_attr, end_attr, start_expected, end_expected):
    g = TimestampDerived(start=start, end=end, date=date)

    assert start_expected == attrgetter(start_attr)(g)
    assert end_expected == attrgetter(end_attr)(g)
