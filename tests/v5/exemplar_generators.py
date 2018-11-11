from .context import tohu
from tohu.v5.primitive_generators import *


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux"),
    Boolean(p=0.3),
    Integer(100, 200),
    Float(low=1.234, high=5.678),
    CharString(length=8),
]

EXEMPLAR_GENERATORS = EXEMPLAR_PRIMITIVE_GENERATORS