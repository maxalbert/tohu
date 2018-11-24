from .context import tohu
from tohu.v6.primitive_generators import *
from .conftest import Quux1Generator, Quux2Generator


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux"),
    Integer(100, 200),
    HashDigest(length=8),
    FakerGenerator(method="name"),
]

EXEMPLAR_DERIVED_GENERATORS = []

EXEMPLAR_CUSTOM_GENERATORS = [Quux1Generator(), Quux2Generator(method="name")]

EXEMPLAR_GENERATORS = EXEMPLAR_PRIMITIVE_GENERATORS + EXEMPLAR_DERIVED_GENERATORS