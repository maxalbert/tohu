import pytest

from .context import tohu
from tohu.v6.tohu_namespace import TohuNamespace, TohuNamespaceError
from tohu.v6.primitive_generators import Constant, Integer, HashDigest
from tohu.v6.derived_generators import Apply, Lookup, SelectMultiple


@pytest.fixture
def g1():
    return Integer(100, 200).set_tohu_name("g1")


@pytest.fixture
def g2():
    return HashDigest(length=6).set_tohu_name("g2")


@pytest.fixture
def xx():
    return Integer(100, 200).set_tohu_name("xx")


@pytest.fixture
def yy():
    return Integer(300, 400).set_tohu_name("yy")


@pytest.fixture
def g3(xx, yy):
    def add(x, y):
        return x + y

    return Apply(add, xx, yy).set_tohu_name("g3")


@pytest.fixture
def g1_anon():
    return Integer(300, 400).set_tohu_name("g1_anon")


@pytest.fixture
def g2_anon():
    return HashDigest(length=8).set_tohu_name("g2_anon")


def test_new_namespace_is_empty():
    ns = TohuNamespace()
    assert len(ns) == 0


def test_add_named_generators(g1, g2):
    ns = TohuNamespace()

    assert len(ns) == 0
    assert g1 not in ns
    assert g2 not in ns

    ns.add_with_name(g1, "bb")

    assert len(ns) == 1
    assert g1 in ns
    assert g2 not in ns

    ns.add_with_name(g2, "aa")

    assert len(ns) == 2
    assert g1 in ns
    assert g2 in ns


def test_add_anonymous_generators(g1_anon, g2_anon):
    ns = TohuNamespace()

    assert len(ns) == 0
    assert g1_anon not in ns
    assert g2_anon not in ns

    ns.add_anonymously(g1_anon)

    assert len(ns) == 1
    assert g1_anon in ns
    assert g2_anon not in ns

    ns.add_anonymously(g2_anon)

    assert len(ns) == 2
    assert g1_anon in ns
    assert g2_anon in ns


def test_add_both_named_and_anonymous_generators(g1, g2, g1_anon, g2_anon):
    ns = TohuNamespace()

    ns.add_with_name(g1, name="bb")
    assert len(ns) == 1
    ns.add_anonymously(g1_anon)
    assert len(ns) == 2
    ns.add_with_name(g2, name="aa")
    assert len(ns) == 3
    ns.add_anonymously(g2_anon)
    assert len(ns) == 4


def test_retrieve_named_generators(g1, g2, g1_anon, g2_anon):
    ns = TohuNamespace()

    ns.add_with_name(g1, name="bb")
    ns.add_anonymously(g1_anon)
    ns.add_with_name(g2, name="aa")
    ns.add_anonymously(g2_anon)
    assert ns["bb"] is g1
    assert ns["aa"] is g2


def test_adding_named_generators_multiple_times(g1):
    ns = TohuNamespace()

    assert len(ns) == 0
    ns.add_with_name(g1, name="aa")
    assert len(ns) == 1
    ns.add_with_name(g1, name="aa")
    assert len(ns) == 1


def test_adding_same_generator_with_different_names_raises_error(g1):
    ns = TohuNamespace()

    ns.add_with_name(g1, name="aa")

    with pytest.raises(TohuNamespaceError, match="Generator already exists with a different name"):
        ns.add_with_name(g1, name="bb")


def test_adding_same_generator_first_with_name_and_then_anonymously_only_adds_it_once(g1):
    ns = TohuNamespace()

    assert len(ns) == 0
    ns.add_with_name(g1, name="aa")
    assert len(ns) == 1
    ns.add_anonymously(g1)
    assert len(ns) == 1

    assert ns["aa"] is g1


def test_adding_same_generator_first_anonymously_and_then_with_explicit_name_raises_error(g1):
    ns = TohuNamespace()
    ns.add_anonymously(g1)

    with pytest.raises(TohuNamespaceError, match="Trying to add named generator which was previously added anonymously"):
        ns.add_with_name(g1, name="aa")


def test_adding_derived_generator_also_adds_its_input_generators(g3):
    ns = TohuNamespace()
    assert len(ns) == 0
    ns.add_with_name(g3, name="aa")
    assert len(ns) == 3
    assert ns["aa"] is g3

    ns = TohuNamespace()
    assert len(ns) == 0
    ns.add_anonymously(g3)
    assert len(ns) == 3


def test_update_from_dict(g1, g3):
    ns = TohuNamespace()
    assert len(ns) == 0
    ns.update_from_dict({"aa": g1, "bb": g3})
    assert len(ns) == 4
    assert ns["aa"] is g1
    assert ns["bb"] is g3


def test_initialise_from_dict(g1, xx, g3):
    # Note that the keys yy and cc should be ignored because their values are not tohu generators.
    d = {"aa": g1, "xx": xx, "yy": 11111, "bb": g3, "cc": None}
    ns = TohuNamespace.from_dict(d)
    assert len(ns) == 4
    assert ns["aa"] is g1
    assert ns["bb"] is g3
    assert ns["xx"] is xx
