import pytest
from unittest.mock import Mock
from .exemplar_generators import EXEMPLAR_GENERATORS, EXEMPLAR_PRIMITIVE_GENERATORS, EXEMPLAR_DERIVED_GENERATORS, EXEMPLAR_CUSTOM_GENERATORS

from .context import tohu
from tohu.v6.primitive_generators import Constant


@pytest.mark.parametrize("g", EXEMPLAR_GENERATORS)
def test_reset_automatically_resets_internal_seed_generator(g, monkeypatch):
    """
    Calling reset on a generator automatically calls reset on its internal seed generator with the same seed.
    """
    monkeypatch.setattr(g.seed_generator, 'reset', Mock())

    g.reset(seed=12345)
    g.seed_generator.reset.assert_called_once_with(12345)

    g.reset(seed=99999)
    g.seed_generator.reset.assert_called_with(99999)


@pytest.mark.parametrize("g", EXEMPLAR_GENERATORS)
def test_reset_returns_the_generator_itself(g):
    """
    Calling reset on a generator returns the generator itself.
    """
    h = g.reset(seed=12345)

    assert h is g


@pytest.mark.parametrize("g", EXEMPLAR_PRIMITIVE_GENERATORS)
def test_primitive_generators_return_consistent_values_when_reset(g):
    """
    Primitive generators produce the same sequence when reset with the same seed.
    """
    g.reset(seed=12345)
    items1 = list(g.generate(num=10))

    g.reset(seed=12345)
    items2 = list(g.generate(num=10))


    g.reset(seed=99999)
    items3 = list(g.generate(num=10))

    g.reset(seed=99999)
    items4 = list(g.generate(num=10))


    assert items1 == items2
    assert items3 == items4

    if not isinstance(g, Constant):
        assert items1 != items3


@pytest.mark.parametrize("g", EXEMPLAR_DERIVED_GENERATORS)
def test_primitive_generators_return_consistent_values_when_reset(g):
    """
    Derived generators produce the same sequence when reset with the same seed,
    and if their input generators are also reset with the same seeds.
    """
    g.reset(seed=12345)
    g.reset_input_generators(seed=33333)
    items1 = list(g.generate(num=10))

    g.reset(seed=12345)
    g.reset_input_generators(seed=33333)
    items2 = list(g.generate(num=10))


    g.reset(seed=99999)
    g.reset_input_generators(seed=66666)
    items3 = list(g.generate(num=10))

    g.reset(seed=99999)
    g.reset_input_generators(seed=66666)
    items4 = list(g.generate(num=10))


    assert items1 == items2
    assert items3 == items4

    assert items1 != items3


@pytest.mark.parametrize("g", EXEMPLAR_CUSTOM_GENERATORS)
def test_custom_generators_return_consistent_values_when_reset(g):
    """
    Custom generators produce the same sequence when reset with the same seed.
    """
    g.reset(seed=12345)
    items1 = list(g.generate(num=10))

    g.reset(seed=12345)
    items2 = list(g.generate(num=10))


    g.reset(seed=99999)
    items3 = list(g.generate(num=10))

    g.reset(seed=99999)
    items4 = list(g.generate(num=10))


    assert items1 == items2
    assert items3 == items4

    assert items1 != items3
