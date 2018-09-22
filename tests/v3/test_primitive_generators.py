from unittest.mock import Mock

from .context import tohu
from tohu.v3.primitive_generators import *


def test_can_register_clones_which_are_automatically_reset():
    """
    Can register clones and these are automatically reset when the parent is reset
    """
    dummy_clone = Mock()

    g = Integer(100, 200)
    g.register_clone(dummy_clone)

    g.reset(seed=12345)

    dummy_clone.reset.assert_called_once_with(12345)