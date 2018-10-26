"""
This module contains helper functions which dispatch
the creation of appropriate generators depending on
the input types.
"""

__all__ = ['SelectOne', 'SelectMultiple']

from .base import TohuBaseGenerator
from .primitive_generators import as_tohu_generator, SelectOnePrimitive, SelectMultiplePrimitive
from .derived_generators import SelectOneDerived, SelectMultipleDerived


def SelectOne(values, p=None):
    if not isinstance(values, TohuBaseGenerator) and not isinstance(p, TohuBaseGenerator):
        return SelectOnePrimitive(values, p)
    else:
        values = as_tohu_generator(values)
        p = as_tohu_generator(p)
        return SelectOneDerived(values, p)


def SelectMultiple(values, num):
    if not isinstance(values, TohuBaseGenerator) and not isinstance(num, TohuBaseGenerator):
        return SelectMultiplePrimitive(values, num)
    else:
        values = as_tohu_generator(values)
        num = as_tohu_generator(num)
        return SelectMultipleDerived(values, num)

