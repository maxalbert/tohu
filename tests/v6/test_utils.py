import datetime as dt
import pandas as pd
import pytest

from .context import tohu
from tohu.v6.utils import ensure_is_date_object, TohuDateError


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


@pytest.mark.parametrize("input", [
    "2018-02-04 11:22:33",
    "2018-02-04 00:00:00",
    dt.datetime(2017, 10, 4, 18, 19, 20),
    dt.datetime(2017, 10, 4, 0, 0, 0),
    pd.Timestamp("2016-12-10 08:10:00"),
    pd.Timestamp("2016-12-10 00:00:00"),
])
def test_wrong_date_input_raises_error(input):
    """
    Inputs of the wrong format or type raise a TohuDateError.
    """
    with pytest.raises(TohuDateError):
        ensure_is_date_object(input)
