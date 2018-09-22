from .context import tohu
from tohu.v3.primitive_generators import Integer
from tohu.v3.derived_generators import *


def add(x, y):
    return x + y


def test_apply_sum_operator():
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


def test_chained_apply_sum_operator():
    g1 = Integer(100, 200)
    g2 = Integer(300, 400)
    g3 = Integer(500, 600)
    g4 = Integer(700, 800)

    h5 = Apply(add, g1, g2)
    h6 = Apply(add, g3, g4)
    h7 = Apply(add, h5, h6)

    items1 = list(g1.generate(num=10, seed=11111))
    items2 = list(g2.generate(num=10, seed=22222))
    items3 = list(g3.generate(num=10, seed=33333))
    items4 = list(g4.generate(num=10, seed=44444))
    items_summed = [a+b+c+d for (a, b, c, d) in zip(items1, items2, items3, items4)]

    items7 = list(h7.generate(num=10))

    assert items7 == items_summed