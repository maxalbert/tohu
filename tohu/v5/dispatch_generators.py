"""
This module contains helper functions which dispatch
the creation of appropriate generators depending on
the input types.
"""

__all__ = ['SelectOne']

from .base import TohuBaseGenerator
from .extras import as_tohu_generator
from .primitive_generators import SelectOnePrimitive
from .derived_generators import SelectOneDerived


def SelectOne(values, p=None):
    if not isinstance(values, TohuBaseGenerator) and not isinstance(p, TohuBaseGenerator):
        return SelectOnePrimitive(values, p)
    else:
        values = as_tohu_generator(values)
        p = as_tohu_generator(p)
        return SelectOneDerived(values, p)
