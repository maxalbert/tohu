from unittest.mock import Mock

from .context import tohu
from tohu.v7.primitive_generators import Integer, HashDigest, FakerGenerator
from tohu.v7.custom_generator.tohu_namespace import TohuNamespace


def test_add_field_generators():
    ns = TohuNamespace()

    aa = Integer(100, 200)
    ns.add_field_generator("aa", aa)
    assert ns.field_names == ["aa"]
    assert ns["aa"].is_clone_of(aa)

    bb = HashDigest(length=8)
    ns.add_field_generator("bb", bb)
    assert ns.field_names == ["aa", "bb"]
    assert ns["aa"].is_clone_of(aa)
    assert ns["bb"].is_clone_of(bb)

    cc = FakerGenerator(method="first_name")
    ns.add_field_generator("cc", cc)
    assert ns.field_names == ["aa", "bb", "cc"]
    assert ns["aa"].is_clone_of(aa)
    assert ns["bb"].is_clone_of(bb)
    assert ns["cc"].is_clone_of(cc)


def test_reset():
    ns = TohuNamespace()
    aa = Mock()
    bb = Mock()
    cc = Mock()
    seed_generator= Mock()
    seed_generator.__next__ = Mock(side_effect=["<seed_1>", "<seed_2>", "<seed_3>"])

    ns.add_field_generator("bb", bb)
    ns.add_field_generator("aa", aa)
    ns.add_field_generator("cc", cc)
    ns.seed_generator = seed_generator

    ns.reset(seed="<master_seed>")

    ns.seed_generator.reset.assert_called_once_with("<master_seed>")
    ns["bb"].reset.assert_called_once_with("<seed_1>")
    ns["aa"].reset.assert_called_once_with("<seed_2>")
    ns["cc"].reset.assert_called_once_with("<seed_3>")
