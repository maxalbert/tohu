from .context import tohu
from tohu.v6.tohu_namespace import TohuNamespace
from tohu.v6.primitive_generators import Integer, HashDigest, FakerGenerator


def test_add_generators_with_explicit_names():
    """
    Generators can be added to the namespace with explicit names.
    """
    g1 = Integer(100, 200)
    g2 = HashDigest(length=8)

    ns = TohuNamespace()

    assert "aa" not in ns
    assert "bb" not in ns

    assert len(ns) == 0
    assert [] == ns.names

    ns.add_generator(g1, name="aa")
    assert len(ns) == 1
    assert ["aa"] == ns.names

    ns.add_generator(g2, name="bb")
    assert len(ns) == 2
    assert ["aa", "bb"] == ns.names

    assert ns["aa"] is g1
    assert ns["bb"] is g2


def test_add_anonymous_generator():
    """
    Generators can be added to the namespace without an explicit name.
    """
    g1 = Integer(100, 200)
    g2 = HashDigest(length=8)

    tohu_id_g1 = g1.tohu_id
    tohu_id_g2 = g2.tohu_id

    ns = TohuNamespace()

    # assert "aa" not in ns
    # assert "bb" not in ns

    assert len(ns) == 0
    ns.add_generator(g1, name=None)
    assert len(ns) == 1
    ns.add_generator(g2, name=None)
    assert len(ns) == 2

    names_expected = [
        f"ANONYMOUS_ANONYMOUS_ANONYMOUS_{tohu_id_g1}",
        f"ANONYMOUS_ANONYMOUS_ANONYMOUS_{tohu_id_g2}",
    ]
    assert names_expected == ns.names

    assert ns[names_expected[0]] is g1
    assert ns[names_expected[1]] is g2


def test_adding_generator_twice_with_the_same_name_ignores_the_second_time():
    ns = TohuNamespace()

    g1 = Integer(100, 200)
    g2 = HashDigest(length=8)

    assert len(ns) == 0

    # Add generators for the first time
    ns.add_generator(g1, "aa")
    ns.add_generator(g2, None)
    assert 2 == len(ns)
    assert 2 == len(ns.names)
    assert "aa" == ns.names[0]
    assert ns.names[1].startswith('ANONYMOUS_ANONYMOUS_ANONYMOUS_')

    # Add generator for the second time with the same names.
    # This should not change anything.
    ns.add_generator(g1, "aa")
    ns.add_generator(g2, None)
    assert 2 == len(ns)
    assert 2 == len(ns.names)
    assert "aa" == ns.names[0]
    assert ns.names[1].startswith('ANONYMOUS_ANONYMOUS_ANONYMOUS_')
