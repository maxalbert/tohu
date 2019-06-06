from unittest.mock import Mock
from .context import tohu

from tohu.v7.primitive_generators import Constant


def test_constant():
    g = Constant("quux")
    expected_values = ["quux", "quux", "quux", "quux", "quux"]
    assert expected_values == g.generate(num=5, seed=99999)


def test_calling_generate_with_and_without_seed():
    g = Constant("quux")
    g.reset = Mock()
    assert not g.reset.called

    # Calling generate() without seed should not call g.reset()
    g.generate(num=5, seed=None)
    assert not g.reset.called

    # Calling generate() with an explicit seed should call g.reset()
    g.generate(num=5, seed=11111)
    g.reset.assert_called_once_with(11111)
