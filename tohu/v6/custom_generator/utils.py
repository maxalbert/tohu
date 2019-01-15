import attr
import pandas as pd
import re

from ..base import TohuBaseGenerator
from ..logging import logger

__all__ = ['get_tohu_items_name', 'make_tohu_items_class']


def make_tohu_items_class(clsname, attr_names):
    """
    Parameters
    ----------
    clsname: string
        Name of the class to be created

    attr_names: list of strings
        Names of the attributes of the class to be created
    """

    item_cls = attr.make_class(clsname, {name: attr.ib() for name in attr_names}, repr=False, cmp=True, frozen=True)

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


def get_tohu_items_name(cls):
    """
    Return a string which defines the name of the namedtuple class which will be used
    to produce items for the custom generator.

    By default this will be the first part of the class name (before '...Generator'),
    for example:

        FoobarGenerator -> Foobar
        QuuxGenerator   -> Quux

    However, it can be set explicitly by the user by defining `__tohu_items_name__`
    in the class definition, for example:

        class Quux(CustomGenerator):
            __tohu_items_name__ = 'MyQuuxItem'
    """
    assert issubclass(cls, TohuBaseGenerator)

    try:
        tohu_items_name = cls.__dict__['__tohu_items_name__']
        logger.debug(f"Using item class name '{tohu_items_name}' (derived from attribute '__tohu_items_name__')")
    except KeyError:
        m = re.match('^(.*)Generator$', cls.__name__)
        if m is not None:
            tohu_items_name = m.group(1)
            logger.debug(f"Using item class name '{tohu_items_name}' (derived from custom generator name)")
        else:
            msg = (
                "Cannot derive class name for items to be produced by custom generator. "
                "Please set '__tohu_items_name__' at the top of the custom generator's "
                "definition or change its name so that it ends in '...Generator'"
            )
            raise ValueError(msg)

    return tohu_items_name