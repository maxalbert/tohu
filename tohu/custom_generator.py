import re
from collections import namedtuple
from tohu.generators import BaseGenerator

__all__ = ["CustomGenerator"]


def get_item_class_name(generator_class_name):
    """
    Given the name of a generator class (such as "FoobarGenerator),
    return the first part of the name before "Generator", which
    will be used for the namedtuple items produced by this generator.

    Examples:
        FoobarGenerator -> Foobar
        QuuxGenerator   -> Quux
    """
    return re.match('^(.*)Generator$', generator_class_name).group(1)


def format_item(item, fmt):
    """
    Return a string containing a concatenation of all
    field values of `item` (separated by commas and
    ending in a newline).

    Example:
        >>> item
        Foobar(a=42, b='foo_01', c=1.234)
        >>> format(item)
        '42,foo_01,1.234'
    """
    return ",".join([format(x) for x in item]) + '\n'


class CustomGenerator:

    def __init__(self, seed=None):
        clsname = get_item_class_name(self.__class__.__name__)
        clsdict = self.__class__.__dict__
        self.field_gens = {name: gen for name, gen in clsdict.items() if isinstance(gen, BaseGenerator)}
        self.item_cls = namedtuple(clsname, self.field_gens.keys())
        self.item_cls.__format__ = format_item
        self.reset(seed)

    def reset(self, seed=None):
        if seed is not None:
            for g in self.field_gens.values():
                g.reset(seed)

    def __next__(self):
        field_values = [next(g) for g in self.field_gens.values()]
        return self.item_cls(*field_values)