import pytest

from .conftest import EXEMPLAR_PRIMITIVE_GENERATORS
from .context import tohu
from tohu.v4.primitive_generators import *
from tohu.v4.derived_generators import *


def add(x, y):
    return x + y


@pytest.mark.parametrize("g", EXEMPLAR_PRIMITIVE_GENERATORS)
def test_spawn_primitive_generators(g):
    """
    Test that primitive generators can be spawned and the spawned versions produce the same elements.
    """
    num_items = 10
    g.reset(seed=12345)

    # Let g generate a few items
    items_g_1 = list(g.generate(num_items))

    # Spawn g and let both generate a few more items
    h = g.spawn()
    items_g_2 = list(g.generate(num_items))
    items_h_2 = list(h.generate(num_items))

    # Reset h and re-generate the full list of items
    h.reset(seed=12345)
    items_h = list(h.generate(2*num_items))

    # Verify that the items generated by h after spawning
    # as well as the full sets of items are identical.
    assert items_h_2 == items_g_2
    assert items_h == items_g_1 + items_g_2


def test_spawn_derived_generators():
    """
    Test that derived generators can be spawned and the spawned versions produce the same elements.
    """
    x = Integer(100, 200)
    y = Integer(300, 400)
    z = Integer(500, 600)
    w = Integer(700, 800)
    g = Apply(add, Apply(add, x, y), Apply(add, z, w))

    x.reset(seed=11111)
    y.reset(seed=22222)
    z.reset(seed=33333)
    w.reset(seed=44444)
    g.reset(seed=12345)

    num_items = 50

    # Let g generate a few items
    items_g_1 = list(g.generate(num_items))

    # Spawn g and let both generate a few more items
    h = g.spawn()
    items_g_2 = list(g.generate(num_items))
    items_h_2 = list(h.generate(num_items))

    # Reset h (as well as its input generators x, y) and re-generate the full list of items
    x.reset(seed=11111)
    y.reset(seed=22222)
    z.reset(seed=33333)
    w.reset(seed=44444)
    h.reset(seed=12345)
    items_h = list(h.generate(2*num_items))

    # Verify that the items generated by h after spawning
    # as well as the full sets of items are identical.
    assert items_h_2 == items_g_2
    assert items_h == items_g_1 + items_g_2


def test_spawn_derived_generators_v2():
    """
    Test that derived generators can be spawned and the spawned versions produce the same elements.
    """

    # This is similar to test_spawn_derived_generators() above but
    # involves slightly more complicated definitions of the generators
    # g and h and also involves constituent generators which have their
    # own random state (e.g. SelectOneFromGenerator).

    seqs = [[10, 11, 12, 13, 14, 15],
            [20, 21, 22, 23, 24, 25],
            [30, 31, 32, 33, 34, 35],
            [40, 41, 42, 43, 44, 45]]

    # Note that we need to define the generator `s` separately so
    # that we can explicitly reset it; otherwise the output of `z`
    # (and thus `g` and `h`) will not be reproducible, even though
    # the output of `g` and `h` will still be consistent with each
    # other (although different from run to run). So the first
    # assert statement at the bottom would still pass, but the
    # second one would fail.
    x = Integer(100, 200)
    y = Integer(300, 400)
    s = SelectOne(seqs)
    z = SelectOneFromGenerator(s)

    g = Apply(add, Apply(add, x, y), z)

    x.reset(seed=11111)
    y.reset(seed=22222)
    s.reset(seed=33333)
    z.reset(seed=44444)
    g.reset(seed=12345)

    num_items = 50

    # Let g generate a few items
    items_g_1 = list(g.generate(num_items))

    # Spawn g and let both generate a few more items
    h = g.spawn()
    items_g_2 = list(g.generate(num_items))
    items_h_2 = list(h.generate(num_items))

    # Reset h (as well as its input generators x, y) and re-generate the full list of items
    x.reset(seed=11111)
    y.reset(seed=22222)
    s.reset(seed=33333)
    z.reset(seed=44444)
    h.reset(seed=12345)
    items_h = list(h.generate(2*num_items))

    # Verify that the items generated by h after spawning
    # as well as the full sets of items are identical.
    assert items_h_2 == items_g_2
    assert items_h == items_g_1 + items_g_2