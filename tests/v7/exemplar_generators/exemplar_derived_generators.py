import os

from .helpers import check_each_generator_class_has_at_least_one_exemplar_instance

from ..context import tohu
from tohu.v7.primitive_generators import Integer
from tohu.v7.derived_generators import Apply, fstr

here = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(here, "..", "..", "..", "tohu", "data")

f1 = lambda x: x ** 2
f2 = lambda x, y: x * 100 + y

g_foo = Integer(100, 200)

EXEMPLAR_DERIVED_GENERATORS = [
    Apply(f1, Integer(100, 200)).set_tohu_name("g_apply_1"),
    Apply(f2, Integer(10, 99), y=Integer(10, 99)).set_tohu_name("g_apply_2"),
    fstr("{g_foo:02d}"),
]


check_each_generator_class_has_at_least_one_exemplar_instance(
    "tohu.v7.derived_generators", EXEMPLAR_DERIVED_GENERATORS, exclude_classes=[]
)
