from .context import tohu
from tohu.v4.primitive_generators import *
from tohu.v4.derived_generators import *

__all__ = ['EXEMPLAR_GENERATORS', 'EXEMPLAR_PRIMITIVE_GENERATORS', 'EXEMPLAR_DERIVED_GENERATORS']

def add(x, y):
    return x + y


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Boolean(p=0.3),
    Constant("quux"),
    FakerGenerator(method="name"),
    Float(12.34, 56.78),
    HashDigest(length=6),
    Integer(100, 200),
    IterateOver('abcdefghijklmnopqrstuvwxyz'),
    SelectOne('abcdefghijklmnopqrstuvwxyz'),
    SelectOne('abcde', p=[0.1, 0.05, 0.7, 0.03, 0.12]),
    Timestamp(date='2018-01-01'),
    ]

EXEMPLAR_DERIVED_GENERATORS = [
    Apply(add, Integer(100, 200), Integer(300, 400)),
    Apply(add, Apply(add, Integer(100, 200), Integer(300, 400)), Apply(add, Integer(500, 600), Integer(700, 800))),
]

EXEMPLAR_CUSTOM_GENERATORS = []

EXEMPLAR_GENERATORS = EXEMPLAR_PRIMITIVE_GENERATORS + EXEMPLAR_DERIVED_GENERATORS + EXEMPLAR_CUSTOM_GENERATORS