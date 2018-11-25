from ..context import tohu
from tohu.v6.primitive_generators import *
from tohu.v6.derived_generators import *


def add(x, y):
    return x + y


EXEMPLAR_DERIVED_GENERATORS = [
    Apply(add, Integer(10, 99).set_tohu_name('xx'), Integer(10, 99).set_tohu_name('yy')),
    Lookup(Integer(1, 5).set_tohu_name('xx'), mapping=Constant({1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e'}).set_tohu_name('mm')),
    SelectMultiple(values=['a', 'b', 'c', 'd', 'e'], num=Integer(1, 5)),
]
