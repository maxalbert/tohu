import os

from .context import tohu
from tohu.v4.primitive_generators import *
from tohu.v4.derived_generators import *
from tohu.v4.dispatch_generators import *

__all__ = ['EXEMPLAR_GENERATORS', 'EXEMPLAR_PRIMITIVE_GENERATORS', 'EXEMPLAR_DERIVED_GENERATORS']

def add(x, y):
    return x + y

here = os.path.abspath(os.path.dirname(__file__))
geojson_filename = os.path.join(here, '..', '..', 'tohu', 'data', 'admin_0_countries.geojson')


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Boolean(p=0.3),
    CharString(length=12, charset='<alphanumeric>'),
    Constant("quux"),
    DigitString(length=20),
    FakerGenerator(method="name"),
    Float(12.34, 56.78),
    #GeoJSONGeolocation(geojson_filename, include_attributes=['name', 'pop_est']),
    HashDigest(length=6),
    Integer(100, 200),
    IterateOver('abcdefghijklmnopqrstuvwxyz'),
    SelectOne('abcdefghijklmnopqrstuvwxyz'),
    SelectOne('abcde', p=[0.1, 0.05, 0.7, 0.03, 0.12]),
    Sequential(prefix='Foobar_', digits=3),
    Timestamp(date='2018-01-01'),
    ]

EXEMPLAR_DERIVED_GENERATORS = [
    Apply(add, Integer(100, 200), Integer(300, 400)),
    Apply(add, Apply(add, Integer(100, 200), Integer(300, 400)), Apply(add, Integer(500, 600), Integer(700, 800))),
]

EXEMPLAR_CUSTOM_GENERATORS = []

EXEMPLAR_GENERATORS = EXEMPLAR_PRIMITIVE_GENERATORS + EXEMPLAR_DERIVED_GENERATORS + EXEMPLAR_CUSTOM_GENERATORS