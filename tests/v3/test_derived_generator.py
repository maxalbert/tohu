from .context import tohu
from tohu.v3.primitive_generators import Integer
from tohu.v3.derived_generators import *


def add(x, y):
    return x + y

def square(x):
    return x * x


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


def test_reattach_parent():
    g1 = Integer(0, 9)
    g2 = Integer(0, 9)

    h = Apply(square, g1)

    g1.reset(seed=12345)
    g2.reset(seed=99999)
    items_g1 = list(g1.generate(num=10))
    items_h1 = list(h.generate(num=10))

    h.rewire({g1: g2})

    g1.reset(seed=12345)
    g2.reset(seed=99999)
    items_g2 = list(g2.generate(num=10))
    items_h2 = list(h.generate(num=10))

    assert items_g1 == [6, 0, 4, 5, 3, 4, 9, 6, 2, 5]
    assert items_h1 == [36, 0, 16, 25, 9, 16, 81, 36, 4, 25]
    assert items_g2 == [1, 4, 8, 3, 5, 6, 3, 4, 6, 9]
    assert items_h2 == [1, 16, 64, 9, 25, 36, 9, 16, 36, 81]