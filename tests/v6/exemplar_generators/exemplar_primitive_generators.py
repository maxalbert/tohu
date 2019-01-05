from .helpers import check_each_generator_class_has_at_least_one_exemplar_instance

from ..context import tohu
from tohu.v6.base import PrimitiveGenerator
from tohu.v6.primitive_generators import Boolean, CharString, Constant, DigitString, Integer, HashDigest, FakerGenerator, Timestamp, Date


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux"),
    Boolean(p=0.8),
    Integer(100, 200),
    CharString(length=12, charset="<alphanumeric_uppercase>"),
    DigitString(length=15),
    HashDigest(length=8),
    FakerGenerator(method="name"),
    Timestamp(start="2018-01-01 11:22:33", end="2019-04-12 20:00:05"),
    Date(start="1999-04-01", end="2000-05-02"),
]


check_each_generator_class_has_at_least_one_exemplar_instance(
    'tohu.v6.primitive_generators',
    EXEMPLAR_PRIMITIVE_GENERATORS
)
