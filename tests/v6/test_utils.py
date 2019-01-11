import datetime as dt
import pandas as pd
import pytest

from .context import tohu
from tohu.v6.utils import ensure_is_date_object, ensure_is_datetime_object, TohuDateError, TohuTimestampError


@pytest.mark.parametrize("input, expected_value", [
    ("2018-02-04", dt.date(2018, 2, 4)),
    ("2017-10-23", dt.date(2017, 10, 23)),
    (dt.date(2016, 11, 28), dt.date(2016, 11, 28)),
    (dt.date(2019, 1, 13), dt.date(2019, 1, 13)),
])
def test_date_from_string_or_date_object(input, expected_value):
    """
    Strings of the form YYYY-MM-DD and datetime.date objects are converted to the expected datetime.date objects.
    """
    d = ensure_is_date_object(input)
    assert d == expected_value


@pytest.mark.parametrize("input, expected_value", [
    (pd.Timestamp('2016-11-28 00:00:00', freq='D'), dt.date(2016, 11, 28)),
])
def test_date_from_pandas_timestamp(input, expected_value):
    """
    Pandas Timestamps that can be interpreted as dates are accepted as valid input.
    """
    d = ensure_is_date_object(input)
    assert d == expected_value


@pytest.mark.parametrize("input", [
    "2018-02-04 11:22:33",
    "2018-02-04 00:00:00",
    dt.datetime(2017, 10, 4, 18, 19, 20),
    dt.datetime(2017, 10, 4, 0, 0, 0),
    pd.Timestamp("2016-12-10 08:10:00"),
    pd.Timestamp("2016-12-10 00:00:00"),  # missing freq='D' attribute
    pd.Timestamp("2016-12-10 11:22:33", freq='D'),  # HH:MM:SS must be all zero
])
def test_wrong_date_input_raises_error(input):
    """
    Inputs of the wrong format or type raise a TohuDateError.
    """
    with pytest.raises(TohuDateError):
        ensure_is_date_object(input)


@pytest.mark.parametrize("input, expected_value", [
    ("2018-02-04 11:22:33", dt.datetime(2018, 2, 4, 11, 22, 33)),
    ("2017-10-23 09:08:07", dt.datetime(2017, 10, 23, 9, 8, 7)),
])
def test_timestamp_from_timestamp_string(input, expected_value):
    """
    Strings of the form YYYY-MM-DD HH:MM:SS are converted to the expected datetime.datetime objects.
    """
    d = ensure_is_datetime_object(input)
    assert d == expected_value


@pytest.mark.parametrize("input, expected_value", [
    (dt.datetime(2018, 2, 4, 11, 22, 33), dt.datetime(2018, 2, 4, 11, 22, 33)),
    (dt.datetime(2017, 10, 23, 9, 8, 7), dt.datetime(2017, 10, 23, 9, 8, 7)),
])
def test_timestamp_from_datetime_object(input, expected_value):
    """
    datetime.datetime objects are returned unchanged
    """
    d = ensure_is_datetime_object(input)
    assert d == expected_value


@pytest.mark.parametrize("input, expected_value", [
    (pd.Timestamp("2018-02-04 11:22:33"), dt.datetime(2018, 2, 4, 11, 22, 33)),
    (pd.Timestamp("2017-10-23 09:08:07"), dt.datetime(2017, 10, 23, 9, 8, 7)),
])
def test_timestamp_from_pandas_timestamp(input, expected_value):
    """
    Pandas Timestamps are are converted to the expected datetime.datetime objects.
    """
    d = ensure_is_datetime_object(input)
    assert d == expected_value


@pytest.mark.parametrize("input, optional_offset, expected_value", [
    ("2018-02-04", None, dt.datetime(2018, 2, 4, 0, 0, 0)),
    ("2017-10-23", None, dt.datetime(2017, 10, 23, 0, 0, 0)),
    ("1999-05-10", dt.timedelta(hours=0), dt.datetime(1999, 5, 10, 0, 0, 0)),
    ("1999-05-10", dt.timedelta(hours=23, minutes=59, seconds=59), dt.datetime(1999, 5, 10, 23, 59, 59)),
])
def test_timestamp_from_date_string(input, optional_offset, expected_value):
    """
    Strings of the form YYYY-MM-DD HH:MM:SS are converted to the expected datetime.datetime objects.
    """
    d = ensure_is_datetime_object(input, optional_offset=optional_offset)
    assert d == expected_value


@pytest.mark.parametrize("input, optional_offset, expected_value", [
    (dt.date(2018, 2, 4), None, dt.datetime(2018, 2, 4, 0, 0, 0)),
    (dt.date(2017, 10, 23), None, dt.datetime(2017, 10, 23, 0, 0, 0)),
    (dt.date(1999, 5, 10), dt.timedelta(hours=0), dt.datetime(1999, 5, 10, 0, 0, 0)),
    (dt.date(1999, 5, 10), dt.timedelta(hours=23, minutes=59, seconds=59), dt.datetime(1999, 5, 10, 23, 59, 59)),
])
def test_timestamp_from_date_object(input, optional_offset, expected_value):
    """
    Datetime.date objects are converted to the expected datetime.datetime objects (including optional offset if given).
    """
    d = ensure_is_datetime_object(input, optional_offset=optional_offset)
    assert d == expected_value


@pytest.mark.parametrize("input, expected_value", [
    ("2018-03-09 04:05:06", dt.datetime(2018, 3, 9, 4, 5, 6)),
    (dt.datetime(2018, 4, 12, 10, 33, 55), dt.datetime(2018, 4, 12, 10, 33, 55)),
    (dt.datetime(2018, 4, 12, 0, 0, 0), dt.datetime(2018, 4, 12, 0, 0, 0)),
    (pd.Timestamp("1999-10-05 11:42:55"), dt.datetime(1999, 10, 5, 11, 42, 55)),
])
def test_optional_offset_is_ignored_for_input_types_that_do_not_support_it(input, expected_value):
    optional_offset = dt.timedelta(hours=23, minutes=59, seconds=59)

    assert ensure_is_datetime_object(input, optional_offset) == expected_value
