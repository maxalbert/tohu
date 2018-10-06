"""
This module is not meant to be imported directly.
Its purpose is to patch the TohuBaseGenerator class
so that its special methods __add__, __mul__ etc.
support other generators as arguments.
"""

from operator import add, mul, gt, ge, lt, le, eq

from .base import TohuBaseGenerator
from .primitive_generators import Constant
from .derived_generators import Apply

__all__ = []


def as_tohu_generator(g):
    """
    If g is a tohu generator, return it unchanged,
    otherwise wrap it in a Constant generator.
    """
    if isinstance(g, TohuBaseGenerator):
        return g
    else:
        return Constant(g)


def add_generators(self, other):
    return Apply(add, self, as_tohu_generator(other))


def radd_generators(self, other):
    return Apply(add, as_tohu_generator(other), self)


def mul_generators(self, other):
    return Apply(mul, self, as_tohu_generator(other))


def rmul_generators(self, other):
    return Apply(mul, as_tohu_generator(other), self)


def eq_generators(self, other):
    return Apply(eq, self, as_tohu_generator(other))


def lt_generators(self, other):
    return Apply(lt, self, as_tohu_generator(other))


def le_generators(self, other):
    return Apply(le, self, as_tohu_generator(other))


def gt_generators(self, other):
    return Apply(gt, self, as_tohu_generator(other))


def ge_generators(self, other):
    return Apply(ge, self, as_tohu_generator(other))


# Patch TohuBaseGenerator with the new methods
TohuBaseGenerator.__add__ = add_generators
TohuBaseGenerator.__radd__ = radd_generators
TohuBaseGenerator.__mul__ = mul_generators
TohuBaseGenerator.__rmul__ = rmul_generators
TohuBaseGenerator.__eq__ = eq_generators
TohuBaseGenerator.__lt__ = lt_generators
TohuBaseGenerator.__le__ = le_generators
TohuBaseGenerator.__gt__ = gt_generators
TohuBaseGenerator.__ge__ = ge_generators
