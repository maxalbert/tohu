"""
This module is not meant to be imported directly.
Its purpose is to patch the TohuBaseGenerator class
so that its special methods __add__, __mul__ etc.
support other generators as arguments.
"""

from operator import add, mul, gt, ge, lt, le, eq

from .base import TohuBaseGenerator
from .primitive_generators import GeoJSONGeolocation
from .derived_generators import GetAttribute

__all__ = []


def split_geolocation(self):
    attributes = ['lon', 'lat'] + self.include_attributes
    return tuple(GetAttribute(self, attr_name) for attr_name in attributes)

GeoJSONGeolocation.split = split_geolocation
