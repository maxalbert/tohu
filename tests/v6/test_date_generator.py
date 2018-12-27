import datetime as dt

from .context import tohu
from tohu.v6.primitive_generators import Date


def test_single_date():
    g = Date(start="2018-01-01", end="2018-01-01")
    dates = g.generate(100, seed=12345)
    assert all([x == dt.date(2018, 1, 1) for x in dates])


def test_date_range():
    g = Date(start="1999-11-28", end="1999-12-01")
    dates = g.generate(1000, seed=12345)

    dates_expected = [
        dt.date(1999, 11, 28),
        dt.date(1999, 11, 29),
        dt.date(1999, 11, 30),
        dt.date(1999, 12, 1),
    ]
    assert set(dates_expected) == set(dates)


def test_start_and_end():
    g = Date(start="1999-11-28", end="1999-12-01")
    assert g.start == dt.date(1999, 11, 28)
    assert g.end == dt.date(1999, 12, 1)
