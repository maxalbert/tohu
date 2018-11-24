from .context import tohu
from tohu.v6.primitive_generators import *
from tohu.v6.derived_generators import *
from .conftest import Quux1Generator, Quux2Generator


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux"),
    Integer(100, 200),
    HashDigest(length=8),
    FakerGenerator(method="name"),
]


def add(x, y):
    return x + y


EXEMPLAR_DERIVED_GENERATORS = [
    Apply(add, Integer(10, 99), Integer(10, 99)),
]

EXEMPLAR_CUSTOM_GENERATORS = [Quux1Generator(), Quux2Generator(method="name")]

EXEMPLAR_GENERATORS = EXEMPLAR_PRIMITIVE_GENERATORS + EXEMPLAR_DERIVED_GENERATORS