import attr
import pandas as pd

from collections import namedtuple

__all__ = ['identity', 'make_tohu_item_class', 'print_generated_sequence']


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


def make_tohu_item_class(clsname, attr_names):
    """
    Parameters
    ----------
    clsname: string
        Name of the class to be created

    attr_names: list of strings
        Names of the attributes of the class to be created
    """

    item_cls = attr.make_class(clsname, {name: attr.ib() for name in attr_names}, repr=False, cmp=True)

    def new_repr(self):
        all_fields = ', '.join([f'{name}={repr(value)}' for name, value in attr.asdict(self).items()])
        return f'{clsname}({all_fields})'

    orig_eq = item_cls.__eq__

    def new_eq(self, other):
        """
        Custom __eq__() method which also allows comparisons with
        tuples and dictionaries. This is mostly for convenience
        during testing.
        """

        if isinstance(other, self.__class__):
            return orig_eq(self, other)
        else:
            if isinstance(other, tuple):
                return attr.astuple(self) == other
            elif isinstance(other, dict):
                return attr.asdict(self) == other
            else:
                return NotImplemented

    item_cls.__repr__ = new_repr
    item_cls.__eq__ = new_eq
    item_cls.keys = lambda self: attr_names
    item_cls.__getitem__ = lambda self, key: getattr(self, key)
    item_cls.as_dict = lambda self: attr.asdict(self)
    item_cls.to_series = lambda self: pd.Series(attr.asdict(self))

    return item_cls
