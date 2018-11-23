from .context import tohu
from tohu.v5.primitive_generators import *


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux"),
    Integer(100, 200),
]

EXEMPLAR_DERIVED_GENERATORS = []

EXEMPLAR_GENERATORS = EXEMPLAR_PRIMITIVE_GENERATORS + EXEMPLAR_DERIVED_GENERATORS