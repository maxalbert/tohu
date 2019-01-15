"""
This module is not meant to be imported directly.
Its purpose is to patch the TohuBaseGenerator class
so that its special methods __add__, __mul__ etc.
support other generators as arguments.
"""

from .base import TohuBaseGenerator
from .primitive_generators import GeoJSONGeolocation, as_tohu_generator
from .derived_generators import Apply, GetAttribute
from operator import add, mul, gt, ge, lt, le, eq

__all__ = []


def check_that_operator_can_be_applied_to_produces_items(op, g1, g2):
    """
    Helper function to check that the operator `op` can be applied to items produced by g1 and g2.
    """
    g1_tmp_copy = g1.spawn()
    g2_tmp_copy = g2.spawn()
    sample_item_1 = next(g1_tmp_copy)
    sample_item_2 = next(g2_tmp_copy)
    try:
        op(sample_item_1, sample_item_2)
    except TypeError:
        raise TypeError(f"Operator '{op.__name__}' cannot be applied to items produced by {g1} and {g2} "
                        f"(which have type {type(sample_item_1)} and {type(sample_item_2)}, respectively)")


def add_generators(self, other):
    check_that_operator_can_be_applied_to_produces_items(add, self, other)
    return Apply(add, self, as_tohu_generator(other))


def radd_generators(self, other):
    check_that_operator_can_be_applied_to_produces_items(add, other, self)
    return Apply(add, as_tohu_generator(other), self)


def mul_generators(self, other):
    check_that_operator_can_be_applied_to_produces_items(mul, self, other)
    return Apply(mul, self, as_tohu_generator(other))


def rmul_generators(self, other):
    check_that_operator_can_be_applied_to_produces_items(mul, other, self)
    return Apply(mul, as_tohu_generator(other), self)


def eq_generators(self, other):
    check_that_operator_can_be_applied_to_produces_items(eq, self, other)
    return Apply(eq, self, as_tohu_generator(other))


def lt_generators(self, other):
    check_that_operator_can_be_applied_to_produces_items(lt, self, other)
    return Apply(lt, self, as_tohu_generator(other))


def le_generators(self, other):
    check_that_operator_can_be_applied_to_produces_items(le, self, other)
    return Apply(le, self, as_tohu_generator(other))


def gt_generators(self, other):
    check_that_operator_can_be_applied_to_produces_items(gt, self, other)
    return Apply(gt, self, as_tohu_generator(other))


def ge_generators(self, other):
    check_that_operator_can_be_applied_to_produces_items(ge, self, other)
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



def split_geolocation(self):
    attributes = ['lon', 'lat'] + self.include_attributes
    return tuple(GetAttribute(self, attr_name) for attr_name in attributes)

GeoJSONGeolocation.split = split_geolocation
