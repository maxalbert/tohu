"""
This module contains helper functions which dispatch
the creation of appropriate generators depending on
the input types.
"""

__all__ = ['Integer', 'Timestamp']

from .base import TohuBaseGenerator
from .primitive_generators import Integer as IntegerPrimitive, Timestamp as TimestampPrimitive
from .derived_generators import Integer as IntegerDerived,Timestamp as TimestampDerived


def Integer(low, high):
    if (not isinstance(low, TohuBaseGenerator) and not isinstance(high, TohuBaseGenerator)):
        return IntegerPrimitive(low, high)
    else:
        return IntegerDerived(low, high)


def Timestamp(*, start=None, end=None, date=None, fmt=None, uppercase=False):
    if (not isinstance(start, TohuBaseGenerator)
        and not isinstance(end, TohuBaseGenerator)
        and not isinstance(date, TohuBaseGenerator)):
        return TimestampPrimitive(start=start, end=end, date=date, fmt=fmt, uppercase=uppercase)
    else:
        return TimestampDerived(start=start, end=end, date=date, fmt=fmt, uppercase=uppercase)
