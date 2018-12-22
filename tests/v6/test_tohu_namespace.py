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
def h1():
    return Integer(300, 400).set_tohu_name("h1")


@pytest.fixture
def h2():
    return HashDigest(length=8).set_tohu_name("h2")


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


def test_add_anonymous_generators(h1, h2):
    ns = TohuNamespace()

    assert len(ns) == 0
    assert h1 not in ns
    assert h2 not in ns

    ns.add_anonymously(h1)

    assert len(ns) == 1
    assert h1 in ns
    assert h2 not in ns

    ns.add_anonymously(h2)

    assert len(ns) == 2
    assert h1 in ns
    assert h2 in ns


def test_add_both_named_and_anonymous_generators(g1, g2, h1, h2):
    ns = TohuNamespace()

    ns.add_with_name(g1, name="bb")
    assert len(ns) == 1
    ns.add_anonymously(h1)
    assert len(ns) == 2
    ns.add_with_name(g2, name="aa")
    assert len(ns) == 3
    ns.add_anonymously(h2)
    assert len(ns) == 4


def test_retrieve_named_generators(g1, g2, h1, h2):
    ns = TohuNamespace()

    ns.add_with_name(g1, name="bb")
    ns.add_anonymously(h1)
    ns.add_with_name(g2, name="aa")
    ns.add_anonymously(h2)
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

    with pytest.raises(TohuNamespaceError, match="Trying to add generator with name which was previously added anonymously"):
        ns.add_with_name(g1, name="aa")
