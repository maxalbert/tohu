import datetime as dt
import pytest

from .context import tohu
from tohu.v6.derived_generators import Timestamp, TimestampError


def test_initialising_with_string_and_timestamp_yields_same_results():
    t_start = dt.datetime(2018, 1, 1, 11, 22, 33)
    t_end = dt.datetime(2018, 1, 1, 12, 23, 34)

    g1 = Timestamp(start="2018-01-01 11:22:33", end="2018-01-01 12:23:34")
    g2 = Timestamp(start=t_start, end=t_end)
    timestamps_1 = g1.generate(100, seed=12345)
    timestamps_2 = g2.generate(100, seed=12345)

    assert all([(x == y) for x, y in zip(timestamps_1, timestamps_2)])


def test_generated_timestamps_are_between_start_and_end_values():
    t_start = dt.datetime(2018, 1, 1, 11, 22, 33)
    t_end = dt.datetime(2018, 1, 1, 12, 23, 34)

    g = Timestamp(start=t_start, end=t_end)
    timestamps = g.generate(100, seed=12345)
    assert all([(t_start <= x <= t_end) for x in timestamps])


def test_can_pass_dates_for_start_and_end():
    """
    If a date of the form "YYYY-MM-DD" is passed for `start` instead of a
    full timestamp, it is interpreted as "YYYY-MM-DD 00:00:00". Similarly,
    if a date is passed for `end` it is interpreted as "YYYY-MM-DD 23:59:59".
    """
    # g1 and g2 should produce the same timestamps
    g1 = Timestamp(start="2018-04-29", end="2018-04-29")
    g2 = Timestamp(start="2018-04-29 00:00:00", end="2018-04-29 23:59:59")

    # g3 and g4 should produce different timestamps than g1 and g2
    g3 = Timestamp(start="2018-04-29 00:00:01", end="2018-04-29 23:59:59")
    g4 = Timestamp(start="2018-04-29 00:00:00", end="2018-04-29 23:59:58")

    timestamps_1 = g1.generate(10000, seed=12345)
    timestamps_2 = g2.generate(10000, seed=12345)
    timestamps_3 = g3.generate(10000, seed=12345)
    timestamps_4 = g3.generate(10000, seed=12345)

    assert all([(x == y) for x, y in zip(timestamps_1, timestamps_2)])
    assert not all([(x == y) for x, y in zip(timestamps_1, timestamps_3)])
    assert not all([(x == y) for x, y in zip(timestamps_1, timestamps_4)])


def test_start_can_be_equal_to_end():
    g = Timestamp(start="2018-01-01 11:22:33", end="2018-01-01 11:22:33")
    timestamps = g.generate(10, seed=12345)
    assert all([x == dt.datetime(2018, 1, 1, 11, 22, 33) for x in timestamps])


def test_raises_error_if_start_is_later_than_end():
    with pytest.raises(TimestampError, match="Latest start value must be before earliest end value"):
        Timestamp(start="2018-01-01 11:22:33", end="2018-01-01 10:09:08")


def test_raises_error_if_start_generator_produces_timestamps_later_than_end_generator():
    g_start = Timestamp(start="2018-01-01", end="2018-01-30")
    g_end = Timestamp(start="2018-01-02", end="2018-01-31")

    with pytest.raises(TimestampError, match="Latest start value must be before earliest end value"):
        Timestamp(start=g_start, end=g_end)
