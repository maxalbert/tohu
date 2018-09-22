from .context import tohu
from tohu.v3.primitive_generators import Integer
from tohu.v3.derived_generators import *


def test_apply_sum_operator():
    def add(x, y):
        return x + y

    g1 = Integer(100, 200)
    g2 = Integer(30, 40)
    h = Apply(add, g1, g2)

    items_g1 = list(g1.generate(num=10, seed=11111))
    items_g2 = list(g2.generate(num=10, seed=22222))
    items_summed = [x + y for (x, y) in zip(items_g1, items_g2)]

    h_after = Apply(add, g1, g2)
    items_g1_after = list(g1.generate(num=10))
    items_g2_after = list(g2.generate(num=10))
    items_summed_after = [x + y for (x, y) in zip(items_g1_after, items_g2_after)]

    items_h = list(h.generate(num=10))
    items_h_after = list(h_after.generate(num=10))

    assert items_h == items_summed
    assert items_h_after == items_summed_after