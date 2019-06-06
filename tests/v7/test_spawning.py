import pytest

from .context import tohu
from tohu.v7.primitive_generators import *

from .exemplar_generators import EXEMPLAR_GENERATORS


@pytest.mark.parametrize("g", EXEMPLAR_GENERATORS)
def test_spawning(g):
    g_spawned = g.spawn()

    # Reset both generators with the same seed and check
    # that they produce the same elements.
    g.reset(seed=99999)
    g_spawned.reset(seed=99999)
    items_g = g.generate(num=10)
    items_g_spawned = g_spawned.generate(num=10)
    assert items_g == items_g_spawned

    # Reset both generators with different seed and check
    # that they produce different elements (to verify that
    # they are independent).
    if not isinstance(g, (Constant, Incremental)):
        g.reset(seed=12345)
        g_spawned.reset(seed=99999)
        items_g = g.generate(num=10)
        items_g_spawned = g_spawned.generate(num=10)
        assert items_g != items_g_spawned

    # Reset both generators with the same seed and
    # check that they produce the same elements again.
    g.reset(seed=44444)
    g_spawned.reset(seed=44444)
    items_g = g.generate(num=10)
    items_g_spawned = g_spawned.generate(num=10)
    assert items_g == items_g_spawned
