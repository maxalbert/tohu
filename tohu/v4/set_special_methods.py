"""
This module is not meant to be imported directly.
Its purpose is to patch the TohuBaseGenerator class
so that its special methods __add__, __mul__ etc.
support other generators as arguments.
"""

from operator import add, mul, gt, ge, lt, le, eq

from .base import TohuBaseGenerator
from .primitive_generators import GeoJSONGeolocation, SelectOnePrimitive, Timestamp, as_tohu_generator
from .derived_generators import Apply, GetAttribute, SelectOneDerived
from .utils import identity

__all__ = []


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


def getattribute_generators(self, name):

    if name == '__isabstractmethod__':
        # Special case which is needed because TohuUltraBaseMeta is
        # derived from ABCMeta and it uses '__isabstractmethod__'
        # to check for abstract methods.
        #
        # TODO: This check should probably be moved to TohuUltraBaseGenerator somewhere.
        return

    if name == '_ipython_canary_method_should_not_exist_':
        # Special case which is needed because IPython uses this attribute internally.
        raise NotImplementedError("Special case needed for IPython")

    return GetAttribute(self, name)

SelectOnePrimitive.__getattr__ = getattribute_generators
SelectOneDerived.__getattr__ = getattribute_generators


def split_geolocation(self):
    attributes = ['lon', 'lat'] + self.include_attributes
    return tuple(GetAttribute(self, attr_name) for attr_name in attributes)

GeoJSONGeolocation.split = split_geolocation
