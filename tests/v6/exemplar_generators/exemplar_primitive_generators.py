from ..context import tohu
from tohu.v6.primitive_generators import *


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux"),
    Integer(100, 200),
    HashDigest(length=8),
    FakerGenerator(method="name"),
]
