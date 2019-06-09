import pytest

from .context import tohu
from tohu.v7.primitive_generators import *

from .exemplar_generators import EXEMPLAR_PRIMITIVE_GENERATORS, EXEMPLAR_DERIVED_GENERATORS, EXEMPLAR_CUSTOM_GENERATORS


@pytest.mark.parametrize("g", EXEMPLAR_PRIMITIVE_GENERATORS + EXEMPLAR_CUSTOM_GENERATORS)
def test_spawn_primitive_and_custom_generators(g):
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


@pytest.mark.parametrize("g", EXEMPLAR_DERIVED_GENERATORS)
def test_spawn_derived_generators(g):
    g_spawned = g.spawn()

    # Reset the original and spawned generator (as well as
    # all their argument generators) with the same seed and
    # check that they produce the same elements
    g.reset(seed=99999)
    g_spawned.reset(seed=99999)
    g._reset_argument_generators(seed=77777)
    g_spawned._reset_argument_generators(seed=77777)

    items_g = g.generate(num=10)
    items_g_spawned = g_spawned.generate(num=10)
    assert items_g == items_g_spawned

    # Reset both generators with different seed and check
    # that they produce different elements (to verify that
    # they are independent). Note that this only works if
    # there is any random state in the derived generator
    # (otherwise the outputs are completely determined by
    # the states of the argument generators).
    if g.has_internal_random_state:
        g.reset(seed=12345)
        g_spawned.reset(seed=99999)
        g._reset_argument_generators(seed=77777)
        g_spawned._reset_argument_generators(seed=77777)
        items_g = g.generate(num=10)
        items_g_spawned = g_spawned.generate(num=10)
        assert items_g != items_g_spawned

    # Reset both generators (incl. argument generators) with the
    # same seed and check that they produce the same elements again.
    g.reset(seed=44444)
    g_spawned.reset(seed=44444)
    g._reset_argument_generators(seed=77777)
    g_spawned._reset_argument_generators(seed=77777)
    items_g = g.generate(num=10)
    items_g_spawned = g_spawned.generate(num=10)
    assert items_g == items_g_spawned

    # Reset both generators with the same seed but reset the
    # argument generators with different seeds, and check that
    # they produce different elements.
    g.reset(seed=55555)
    g_spawned.reset(seed=55555)
    g._reset_argument_generators(seed=77777)
    g_spawned._reset_argument_generators(seed=88888)
    items_g = g.generate(num=10)
    items_g_spawned = g_spawned.generate(num=10)
    assert items_g != items_g_spawned
