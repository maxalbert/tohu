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