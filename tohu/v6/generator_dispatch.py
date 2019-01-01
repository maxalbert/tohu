"""
This module contains helper functions which dispatch
the creation of appropriate generators depending on
the input types.
"""

__all__ = ['Timestamp']

from .base import TohuBaseGenerator
from .primitive_generators import TimestampPrimitive
from .derived_generators import TimestampDerived


def Timestamp(*, start=None, end=None, date=None, fmt=None, uppercase=False):
    if (not isinstance(start, TohuBaseGenerator)
        and not isinstance(end, TohuBaseGenerator)
        and not isinstance(date, TohuBaseGenerator)):
        return TimestampPrimitive(start=start, end=end, date=date, fmt=fmt, uppercase=uppercase)
    else:
        return TimestampDerived(start=start, end=end, date=date, fmt=fmt, uppercase=uppercase)
