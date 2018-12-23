import pytest

from .context import tohu
from tohu.v6.tohu_namespace import TohuNamespace, TohuNamespaceError
from tohu.v6.primitive_generators import Constant, Integer, HashDigest
from tohu.v6.derived_generators import Apply, Lookup, SelectMultiple


def test_new_namespace_is_empty():
    ns = TohuNamespace()
    assert len(ns) == 0


def test_add_generators_with_explicit_names():
    """
    Generators can be added to the namespace with explicit names.
    """
    g1 = Integer(100, 200)
    g2 = HashDigest(length=8)

    ns = TohuNamespace()
    assert len(ns) == 0
    ns["aa"] = g1
    assert len(ns) == 1
    ns["bb"] = g2
    assert len(ns) == 2

    assert ns.all_generators == {g1: "aa", g2: "bb"}


def test_adding_same_generator_with_different_name_should_create_clone():
    """
    Adding the same generator with a different name should create a clone instead.
    """
    g = Integer(100, 200)

    ns = TohuNamespace()
    assert len(ns) == 0
    ns["aa"] = g
    assert len(ns) == 1
    ns["bb"] = g
    assert len(ns) == 2

    assert ns["aa"] is g
    assert ns["bb"] is not g
    assert ns["bb"].parent is g


def test_adding_derived_generators_also_adds_all_input_generators():
    def add(x, y):
        return x + y
    xx = Integer(100, 200)
    yy = Integer(300, 400)
    g = Apply(add, xx, yy)

    ns = TohuNamespace()
    assert len(ns) == 0
    ns["aa"] = g
    assert len(ns) == 3
    assert ns.all_generators == {xx: None, yy: None, g: "aa"}