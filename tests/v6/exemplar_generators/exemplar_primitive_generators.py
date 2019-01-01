from ..context import tohu
from tohu.v6.primitive_generators import Constant, Integer, HashDigest, FakerGenerator, Timestamp, DatePrimitive


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux"),
    Integer(100, 200),
    HashDigest(length=8),
    FakerGenerator(method="name"),
    Timestamp(start="2018-01-01 11:22:33", end="2019-04-12 20:00:05"),
    DatePrimitive(start="1999-04-01", end="2000-05-02"),
]
