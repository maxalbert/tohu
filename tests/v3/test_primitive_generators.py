import pytest
from unittest.mock import Mock

from .context import tohu
from tohu.v3.primitive_generators import *


@pytest.mark.parametrize("g", [
    Constant("quux"),
    Integer(100, 200),
    HashDigest(length=6),
    FakerGenerator(method="name"),
    IterateOver('abcde'),
    SelectOne('abcde'),
])
def test_can_register_clones_which_are_automatically_reset(g):
    """
    Can register clones and these are automatically reset when the parent is reset
    """
    dummy_clone_1 = Mock()
    dummy_clone_2 = Mock()
    g.register_clone(dummy_clone_1)
    g.register_clone(dummy_clone_2)

    g.reset(seed=12345)
    dummy_clone_1.reset.assert_called_once_with(12345)
    dummy_clone_2.reset.assert_called_once_with(12345)

    g.reset(seed=99999)
    dummy_clone_1.reset.assert_called_with(99999)
    dummy_clone_2.reset.assert_called_with(99999)