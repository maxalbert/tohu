from unittest.mock import Mock

from .context import tohu
from tohu.v7.primitive_generators import Integer, HashDigest, FakerGenerator
from tohu.v7.custom_generator.tohu_namespace import TohuNamespace


def test_add_field_generators():
    ns = TohuNamespace("Quux")
    assert ns.tohu_items_cls.__name__ == "Quux"
    assert ns.tohu_items_cls.field_names == []

    aa = Integer(100, 200)
    ns.add_field_generator("aa", aa)
    assert ns.field_names == ["aa"]
    assert ns["aa"].is_clone_of(aa)
    assert ns.tohu_items_cls.field_names == ["aa"]

    bb = HashDigest(length=8)
    ns.add_field_generator("bb", bb)
    assert ns.field_names == ["aa", "bb"]
    assert ns["aa"].is_clone_of(aa)
    assert ns["bb"].is_clone_of(bb)
    assert ns.tohu_items_cls.field_names == ["aa", "bb"]

    cc = FakerGenerator(method="first_name")
    ns.add_field_generator("cc", cc)
    assert ns.field_names == ["aa", "bb", "cc"]
    assert ns["aa"].is_clone_of(aa)
    assert ns["bb"].is_clone_of(bb)
    assert ns["cc"].is_clone_of(cc)
    assert ns.tohu_items_cls.field_names == ["aa", "bb", "cc"]


def test_reset():
    ns = TohuNamespace("Quux")
    aa = Mock()
    bb = Mock()
    cc = Mock()
    seed_generator = Mock()
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


def test_next_item():
    ns = TohuNamespace("Quux")
    aa = Mock(__next__=Mock(side_effect=[11, 22, 33]))
    bb = Mock(__next__=Mock(side_effect=["foo", "bar", "baz"]))
    cc = Mock(__next__=Mock(side_effect=["z", "y", "x"]))
    aa.clone.return_value = aa
    bb.clone.return_value = bb
    cc.clone.return_value = cc

    ns.add_field_generator("bb", bb)
    ns.add_field_generator("aa", aa)
    ns.add_field_generator("cc", cc)

    assert next(ns) == {"bb": "foo", "aa": 11, "cc": "z"}
    assert next(ns) == {"bb": "bar", "aa": 22, "cc": "y"}
    assert next(ns) == {"bb": "baz", "aa": 33, "cc": "x"}


# TODO: we should probably also check that the state of generators
# transferred correctly when spawning a TohuNamespace instance.
def test_spawn():
    ns = TohuNamespace("Quux")
    aa_first_clone = Mock()
    bb_first_clone = Mock()
    aa_second_clone = Mock()
    bb_second_clone = Mock()
    aa = Mock(clone=Mock(side_effect=[aa_first_clone, aa_second_clone]))
    bb = Mock(clone=Mock(side_effect=[bb_first_clone, bb_second_clone]))
    aa_first_clone.parent = aa_second_clone.parent = aa
    bb_first_clone.parent = bb_second_clone.parent = bb

    ns.add_field_generator("aa", aa)
    ns.add_field_generator("bb", bb)
    assert ns["aa"] is aa_first_clone
    assert ns["bb"] is bb_first_clone

    ns_spawned = ns.spawn()
    assert ns_spawned["aa"] is aa_second_clone
    assert ns_spawned["bb"] is bb_second_clone


def test_update_from_dict():
    ns = TohuNamespace("Quux")
    the_dict = {"aa": Integer(100, 200), "bb": "<this_is_not_a_tohu_generator", "cc": HashDigest(length=6)}
    ns.update_from_dict(the_dict)
    assert ns.field_names == ["aa", "cc"]
