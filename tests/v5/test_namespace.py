import pytest

from .context import tohu
from tohu.v5.namespace import TohuNamespace, TohuNamespaceError
from tohu.v5.primitive_generators import Integer, HashDigest, FakerGenerator
from tohu.v5.derived_generators import Apply


def test_add_generator_with_explicit_name():
    """
    Adding a generator with an explicit name to the namespace.
    """
    n = TohuNamespace()
    g = Integer(100, 200)
    assert len(n) == 0
    n.add_generator(g, name="foobar")
    assert len(n) == 1
    assert n["foobar"] == g


def test_contains():
    n = TohuNamespace()
    g1 = Integer(100, 200)
    g2 = Integer(100, 200)
    n.add_generator(g1)
    assert g1 in n
    assert g2 not in n


def test_add_generator_without_explicit_name():
    """

    """
    n = TohuNamespace()
    g = Integer(100, 200)
    assert len(n) == 0
    n.add_generator(g, name=None)
    assert len(n) == 1
    assert n[f"ANONYMOUS_ANONYMOUS_ANONYMOUS_{g.tohu_id}"] == g


def test_add_generator_twice_with_the_same_explicit_name():
    """
    """
    n = TohuNamespace()
    g = Integer(100, 200)
    assert len(n) == 0
    n.add_generator(g, name="foobar")
    assert len(n) == 1
    n.add_generator(g, name="foobar")
    assert len(n) == 1
    assert n["foobar"] == g


def test_add_generator_twice_with_first_name_anonymous():
    """
    """
    n = TohuNamespace()
    g = Integer(100, 200)
    assert len(n) == 0
    n.add_generator(g, name=None)
    assert len(n) == 1
    n.add_generator(g, name="foobar")
    assert len(n) == 1
    assert n["foobar"] == g


def test_add_generator_twice_with_second_name_anonymous():
    """
    """
    n = TohuNamespace()
    g = Integer(100, 200)
    assert len(n) == 0
    n.add_generator(g, name="foobar")
    assert len(n) == 1
    n.add_generator(g, name=None)
    assert len(n) == 1
    assert n["foobar"] == g


def test_add_generator_twice_with_both_names_anonymous():
    """
    """
    n = TohuNamespace()
    g = Integer(100, 200)
    assert len(n) == 0
    n.add_generator(g, name=None)
    assert len(n) == 1
    n.add_generator(g, name=None)
    assert len(n) == 1
    assert n[f"ANONYMOUS_ANONYMOUS_ANONYMOUS_{g.tohu_id}"] == g


def test_add_two_different_generators_with_the_same_name():
    """
    """
    n = TohuNamespace()
    g1 = Integer(100, 200)
    g2 = Integer(100, 200)
    assert len(n) == 0
    n.add_generator(g1, name="foobar")
    assert len(n) == 1
    with pytest.raises(TohuNamespaceError):
        n.add_generator(g2, name="foobar")


def test_spawning_of_namespace_with_a_single_generator():
    n = TohuNamespace()
    g = Integer(100, 200)
    n.add_generator(g, "foobar")

    n_spawned = n.spawn()
    assert isinstance(n_spawned, TohuNamespace)
    assert len(n_spawned) == 1
    assert isinstance(n_spawned["foobar"], Integer)
    assert n_spawned["foobar"] is not g


def test_spawning_of_namespace_with_multiple_independent_generators():
    n = TohuNamespace()
    g1 = Integer(100, 200)
    g2 = HashDigest(length=8)
    g3 = FakerGenerator(method="name")
    n.add_generator(g1, "g1")
    n.add_generator(g2, "g2")
    n.add_generator(g3, "g3")

    n_spawned = n.spawn()
    assert isinstance(n_spawned, TohuNamespace)
    assert len(n_spawned) == 3
    assert isinstance(n_spawned["g1"], Integer)
    assert isinstance(n_spawned["g2"], HashDigest)
    assert isinstance(n_spawned["g3"], FakerGenerator)
    assert n_spawned["g1"] is not g1
    assert n_spawned["g2"] is not g2
    assert n_spawned["g3"] is not g3


def test_spawning_of_namespace_with_cloned_generator():
    n = TohuNamespace()
    g1 = Integer(100, 200)
    g2 = g1.clone()
    g3 = g1.clone()
    n.add_generator(g1, "g1")
    n.add_generator(g2, "g2")
    n.add_generator(g3, "g3")

    n_spawned = n.spawn()
    assert isinstance(n_spawned, TohuNamespace)
    assert len(n_spawned) == 3
    assert isinstance(n_spawned["g1"], Integer)
    assert isinstance(n_spawned["g2"], Integer)
    assert isinstance(n_spawned["g3"], Integer)
    assert n_spawned["g1"] is not g1
    assert n_spawned["g2"] is not g2
    assert n_spawned["g3"] is not g3

    assert n["g2"].parent is g1
    assert n["g3"].parent is g1

    assert n_spawned["g2"].parent is n_spawned["g1"]
    assert n_spawned["g3"].parent is n_spawned["g1"]


def test_spawning_of_namespace_with_derived_generator():
    n = TohuNamespace()
    aa = Integer(100, 200).set_tohu_name("aa")
    bb = Integer(300, 400).set_tohu_name("bb")
    cc = Apply(lambda x, y: x+y, aa, bb)
    n.add_generator(aa, "aa")
    n.add_generator(bb, "bb")
    n.add_generator(cc, "cc")

    n_spawned = n.spawn()
    assert isinstance(n_spawned, TohuNamespace)
    assert len(n_spawned) == 3
    assert isinstance(n_spawned["aa"], Integer)
    assert isinstance(n_spawned["bb"], Integer)
    assert isinstance(n_spawned["cc"], Apply)
    assert n_spawned["aa"] is not aa
    assert n_spawned["bb"] is not bb
    assert n_spawned["cc"] is not cc

    assert n_spawned["cc"]._input_generators == [n_spawned["aa"], n_spawned["bb"]]
    assert n_spawned["cc"]._constituent_generators[0].parent == n_spawned["aa"]
    assert n_spawned["cc"]._constituent_generators[1].parent == n_spawned["bb"]
