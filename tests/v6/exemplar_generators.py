from .context import tohu
from tohu.v6.primitive_generators import *
from .conftest import QuuxGenerator1, QuuxGenerator2


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux"),
    Integer(100, 200),
    HashDigest(length=8),
    FakerGenerator(method="name"),
]

EXEMPLAR_DERIVED_GENERATORS = []

EXEMPLAR_CUSTOM_GENERATORS = [QuuxGenerator1(), QuuxGenerator2(method="name")]

EXEMPLAR_GENERATORS = EXEMPLAR_PRIMITIVE_GENERATORS + EXEMPLAR_DERIVED_GENERATORS