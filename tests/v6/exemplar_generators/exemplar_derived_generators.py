from .helpers import check_each_generator_class_has_at_least_one_exemplar_instance

from ..context import tohu
from tohu.v6.primitive_generators import (
    Constant,
    Integer,
    Timestamp as TimestampPrimitive,
)
from tohu.v6.derived_generators import (
    DerivedGenerator,
    Apply,
    Integer as IntegerDerived,
    Lookup,
    SelectOne,
    SelectMultiple,
    Tee,
    Timestamp as TimestampDerived,
)


def add(x, y):
    return x + y


EXEMPLAR_DERIVED_GENERATORS = [
    Apply(add, Integer(10, 99).set_tohu_name("xx"), Integer(10, 99).set_tohu_name("yy")),
    IntegerDerived(low=Constant(10), high=Integer(100, 200)),
    Lookup(
        Integer(1, 5).set_tohu_name("xx"),
        mapping=Constant({1: "a", 2: "b", 3: "c", 4: "d", 5: "e"}).set_tohu_name("mm"),
    ),
    SelectOne(values=["a", "b", "c", "d", "e"]),
    SelectMultiple(values=["a", "b", "c", "d", "e"], num=Integer(1, 5)),
    Tee(IntegerDerived(low=Integer(100, 200), high=Integer(300, 400)), num=Integer(1, 8)),
    TimestampDerived(
        start=TimestampPrimitive(start="2018-01-01 11:22:33", end="2018-03-04 20:19:18"),
        end=TimestampPrimitive(start="2018-05-06 09:08:07", end="2018-10-01 14:55:33"),
    ),
]


check_each_generator_class_has_at_least_one_exemplar_instance(
    "tohu.v6.derived_generators",
    EXEMPLAR_DERIVED_GENERATORS,
    exclude_classes=[DerivedGenerator],
)
