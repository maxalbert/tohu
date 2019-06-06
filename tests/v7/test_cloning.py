import pytest
from unittest.mock import Mock

from .exemplar_generators import EXEMPLAR_GENERATORS


@pytest.mark.parametrize("g", EXEMPLAR_GENERATORS)
def test_cloned_generators_are_reset_automatically_by_parent(g):
    g_cloned = g.clone()
    assert g_cloned.is_clone_of(g)

    g_cloned.reset = Mock()
    g.reset(seed=99999)
    g_cloned.reset.assert_called_with(99999)

    g.reset(seed=12345)
    g_cloned.reset.assert_called_with(12345)


@pytest.mark.parametrize("g", EXEMPLAR_GENERATORS)
def test_cloned_generators_produce_the_same_elements(g):
    g_cloned = g.clone()
    assert g_cloned.is_clone_of(g)

    # Reset g and check that this
    g.reset(seed=99999)
    items_g = g.generate(num=10)
    items_g_cloned = g_cloned.generate(num=10)
    assert items_g == items_g_cloned

    # Reset both generators with a different seed and
    # check that they produce the same elements again.
    g.reset(seed=44444)
    g_cloned.reset(seed=44444)
    items_g = g.generate(num=10)
    items_g_cloned = g_cloned.generate(num=10)
    assert items_g == items_g_cloned


def test_adding_duplicate_clone_raises_error(dummy_generator):
    g_spawned = dummy_generator.spawn()
    dummy_generator.register_clone(g_spawned)
    with pytest.raises(RuntimeError, match="Duplicate clone added"):
        dummy_generator.register_clone(g_spawned)