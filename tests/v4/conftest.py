from .context import tohu
from tohu.v4.primitive_generators import *

EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux"),
    Integer(100, 200),
    HashDigest(length=6),
    FakerGenerator(method="name"),
    IterateOver('abcdefghijklmnopqrstuvwxyz'),
    SelectOne('abcdefghijklmnopqrstuvwxyz'),
    SelectOne('abcde', p=[0.1, 0.05, 0.7, 0.03, 0.12]),
    ]


EXEMPLAR_GENERATORS = EXEMPLAR_PRIMITIVE_GENERATORS