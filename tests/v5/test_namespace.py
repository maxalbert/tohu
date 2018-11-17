import pytest

from .context import tohu
from tohu.v5.namespace import Namespace, TohuNamespaceError
from tohu.v5.primitive_generators import Integer


def test_add_generator_with_explicit_name():
    """
    Adding a generator with an explicit name to the namespace.
    """
    n = Namespace()
    g = Integer(100, 200)
    assert len(n) == 0
    n.add_generator(g, name="foobar")
    assert len(n) == 1
    assert n["foobar"] == g


def test_add_generator_without_explicit_name():
    """

    """
    n = Namespace()
    g = Integer(100, 200)
    assert len(n) == 0
    n.add_generator(g, name=None)
    assert len(n) == 1
    assert n[f"ANONYMOUS_ANONYMOUS_ANONYMOUS_{g.tohu_id}"] == g


def test_add_generator_twice_with_the_same_explicit_name():
    """
    """
    n = Namespace()
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
    n = Namespace()
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
    n = Namespace()
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
    n = Namespace()
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
    n = Namespace()
    g1 = Integer(100, 200)
    g2 = Integer(100, 200)
    assert len(n) == 0
    n.add_generator(g1, name="foobar")
    assert len(n) == 1
    with pytest.raises(TohuNamespaceError):
        n.add_generator(g2, name="foobar")
