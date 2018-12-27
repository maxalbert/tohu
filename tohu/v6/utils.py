import datetime as dt
import pandas as pd
from collections import namedtuple

__all__ = ['ensure_is_date_object', 'ensure_is_datetime_object', 'identity', 'print_generated_sequence', 'parse_date_string', 'parse_datetime_string']


def identity(x):
    """
    Helper function which returns its argument unchanged.
    That is, `identity(x)` returns `x` for any input `x`.
    """
    return x


def print_generated_sequence(gen, num, *, sep=", ", fmt='', seed=None):
    """
    Helper function which prints a sequence of `num` items
    produced by the random generator `gen`.
    """
    if seed:
       gen.reset(seed)

    elems = [format(next(gen), fmt) for _ in range(num)]
    sep_initial = "\n\n" if '\n' in sep else " "
    print("Generated sequence:{}{}".format(sep_initial, sep.join(elems)))


def make_dummy_tuples(chars='abcde'):
    """
    Helper function to create a list of namedtuples which are useful
    for testing and debugging (especially of custom generators).

    Example
    -------
    >>> make_dummy_tuples(chars='abcd')
    [Quux(x='AA', y='aa'),
     Quux(x='BB', y='bb'),
     Quux(x='CC', y='cc'),
     Quux(x='DD', y='dd')]
    """
    Quux = namedtuple('Quux', ['x', 'y'])
    some_tuples = [Quux((c*2).upper(), c*2) for c in chars]
    return some_tuples


class TohuDateError(Exception):
    """
    Custom exception
    """


def parse_date_string(s):
    try:
        date = dt.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise TohuDateError(
            "If input is a string, it must represent a timestamp of the form 'YYYY-MM-DD HH:MM:SS' "
            f"or a date of the form YYYY-MM-DD. Got: '{s}'"
        )
    return date


def ensure_is_date_object(x):
    error_msg = f"Cannot convert input to date object: {x} (type: {type(x)})"

    if isinstance(x, dt.date):
        if isinstance(x, dt.datetime):
            raise TohuDateError(error_msg)
        else:
            return x
    elif isinstance(x, str):
        return parse_date_string(x)
    else:
        raise TohuDateError(error_msg)


class TohuTimestampError(Exception):
    """
    Custom exception
    """


def is_date_object(x):
    return isinstance(x, dt.date) and not isinstance(x, dt.datetime)


def is_date_string(x):
    if not isinstance(x, str):
        return False
    else:
        try:
            dt.datetime.strptime(x, "%Y-%m-%d")
            return True
        except ValueError:
            return False


def parse_datetime_string(s, optional_offset=None):
    try:
        ts = dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        optional_offset = optional_offset or dt.timedelta(seconds=0)
        try:
            ts = dt.datetime.strptime(s, "%Y-%m-%d") + optional_offset
        except ValueError:
            raise ValueError(
                "If input is a string, it must represent a timestamp of the form 'YYYY-MM-DD HH:MM:SS' "
                f"or a date of the form YYYY-MM-DD. Got: '{s}'"
            )
    return ts


def ensure_is_datetime_object(x, optional_offset=None):
    if optional_offset is not None and not (is_date_object(x) or is_date_string(x)):
        raise TohuTimestampError(
            "Nonzero optional_offset values are only allowed with inputs of type "
            f"datetime.date or strings of the form 'YYYY-MM-DD'. Got: {x}")

    error_msg = f"Cannot convert input to datetime object: {x} (type: {type(x)})"

    if isinstance(x, dt.datetime):
        return x
    elif isinstance(x, dt.date):
        optional_offset = optional_offset or dt.timedelta(seconds=0)
        return dt.datetime(x.year, x.month, x.day) + optional_offset
    elif isinstance(x, str):
        return parse_datetime_string(x, optional_offset)
    else:
        raise TohuTimestampError(error_msg)
