from .context import tohu
from tohu.v5.primitive_generators import *
from tohu.v5.derived_generators import *


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux"),
    Boolean(p=0.3),
    Integer(100, 200),
    Float(low=1.234, high=5.678),
    CharString(length=8),
    DigitString(length=10),
    HashDigest(length=8),
    FakerGenerator(method="name"),
]

EXEMPLAR_DERIVED_GENERATORS = [
    Apply(lambda x, y: x + y, Integer(100, 200), Integer(300, 400)),
    Lookup(Integer(1, 5), {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e'}),
    SelectOneDerived(Constant(['a', 'b', 'c'])),
]

EXEMPLAR_GENERATORS = EXEMPLAR_PRIMITIVE_GENERATORS + EXEMPLAR_DERIVED_GENERATORS