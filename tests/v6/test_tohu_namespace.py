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


def test_complex_dependencies():
    mapping = {
        1: ['a', 'aa', 'aaa', 'aaaa', 'aaaaa'],
        2: ['b', 'bb', 'bbb', 'bbbb', 'bbbbb'],
        3: ['c', 'cc', 'ccc', 'cccc', 'ccccc'],
    }

    n_vals = Integer(1, 5)
    xx = Integer(1, 3)
    h = Lookup(xx, mapping=mapping)
    g = SelectMultiple(h, num=n_vals)

    ns = TohuNamespace()
    ns["aa"] = n_vals
    ns["bb"] = g

    assert 5 == len(ns)
    assert ns["aa"] is n_vals
    assert ns["bb"] is g
    assert xx in ns
    assert h in ns


def test_spawning_of_namespace_with_independent_generators():
    g1 = Integer(100, 200)
    g2 = HashDigest(length=8)

    ns = TohuNamespace()
    ns["aa"] = g1
    ns["bb"] = g2

    ns_spawned = ns.spawn()
    assert isinstance(ns_spawned["aa"], Integer)
    assert isinstance(ns_spawned["bb"], HashDigest)


def test_spawning_of_namespace_with_clone():
    g = Integer(100, 200)

    ns = TohuNamespace()
    ns["aa"] = g
    ns["bb"] = g
    assert ns["bb"].parent is ns["aa"]

    ns_spawned = ns.spawn()
    assert len(ns_spawned) == 2
    assert isinstance(ns_spawned["aa"], Integer)
    assert isinstance(ns_spawned["bb"], Integer)
    assert ns_spawned["bb"].parent is ns_spawned["aa"]


def test_spawning_of_namespace_with_complex_dependencies():
    mapping = {
        1: ['a', 'aa', 'aaa', 'aaaa', 'aaaaa'],
        2: ['b', 'bb', 'bbb', 'bbbb', 'bbbbb'],
        3: ['c', 'cc', 'ccc', 'cccc', 'ccccc'],
    }

    n_vals = Integer(1, 5)
    xx = Integer(1, 3)
    h = Lookup(xx, mapping=mapping)
    g = SelectMultiple(h, num=n_vals)

    ns = TohuNamespace()
    ns["aa"] = n_vals
    ns["xx"] = xx
    ns["bb"] = g
    assert len(ns) == 5

    ns_spawned = ns.spawn()
    assert len(ns_spawned) == 5
    assert ns_spawned["bb"].input_generators[0].input_generators is ns_spawned["xx"]
    assert ns_spawned["bb"].input_generators[1] is ns_spawned["aa"]