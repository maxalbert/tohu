import datetime as dt
from collections import namedtuple

__all__ = ['identity', 'print_generated_sequence']


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