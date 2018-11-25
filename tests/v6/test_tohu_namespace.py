import pytest

from unittest.mock import Mock

from .context import tohu
from tohu.v6.tohu_namespace import TohuNamespace, TohuNamespaceError
from tohu.v6.primitive_generators import Constant, Integer, HashDigest
from tohu.v6.derived_generators import Apply, Lookup, SelectMultiple


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
    assert [] == ns.keys()

    ns.add_generator(g1, name="aa")
    assert len(ns) == 1
    assert ["aa"] == ns.keys()

    ns.add_generator(g2, name="bb")
    assert len(ns) == 2
    assert ["aa", "bb"] == ns.keys()

    assert ns["aa"] is g1
    assert ns["bb"] is g2


def test_add_anonymous_generator():
    """
    Generators can be added to the namespace without an explicit name.
    """
    g1 = Integer(100, 200).set_tohu_name("g1")
    g2 = HashDigest(length=8).set_tohu_name("g2")

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
        f"ANONYMOUS_ANONYMOUS_ANONYMOUS_g1",
        f"ANONYMOUS_ANONYMOUS_ANONYMOUS_g2",
    ]
    assert names_expected == ns.keys()

    assert ns[names_expected[0]] is g1
    assert ns[names_expected[1]] is g2


def test_adding_generator_twice_with_the_same_name_ignores_the_second_time():
    ns = TohuNamespace()

    g1 = Integer(100, 200).set_tohu_name("g1")
    g2 = HashDigest(length=8).set_tohu_name("g2")
    expected_names = ["aa", "ANONYMOUS_ANONYMOUS_ANONYMOUS_g2"]

    assert len(ns) == 0

    # Add generators for the first time
    ns.add_generator(g1, "aa")
    ns.add_generator(g2, None)
    assert 2 == len(ns)
    assert 2 == len(ns.keys())
    assert expected_names == ns.keys()

    # Add generator for the second time with the same names.
    # This should not change anything.
    ns.add_generator(g1, "aa")
    ns.add_generator(g2, None)
    assert 2 == len(ns)
    assert 2 == len(ns.keys())
    assert expected_names == ns.keys()


def test_adding_generators_twice_with_different_names_raises_error():
    ns = TohuNamespace()
    g1 = Integer(100, 200).set_tohu_name("g1")
    g2 = HashDigest(length=8).set_tohu_name("g2")
    expected_error_msg = "because it already exists with a different name"

    assert len(ns) == 0

    # Add g1 for the first time (with an explicit name)
    ns.add_generator(g1, name="aa")
    assert ["aa"] == ns.keys()

    # Try to add g1 again with a different name
    with pytest.raises(TohuNamespaceError, match=expected_error_msg):
        ns.add_generator(g1, name="aa_new")
    assert ["aa"] == ns.keys()

    # Adding g1 again anonymously should succeed but not add the generator again
    ns.add_generator(g1, name=None)
    assert ["aa"] == ns.keys()

    # Add g2 for the first time (anonymously)
    ns.add_generator(g2, name=None)
    assert ["aa", "ANONYMOUS_ANONYMOUS_ANONYMOUS_g2"] == ns.keys()

    # Adding g2 again with an explicit name should update the name
    ns.add_generator(g2, name="g2_new")
    assert ["aa", "g2_new"] == ns.keys()


def test_adding_derived_generators_also_adds_their_input_generators():
    ns = TohuNamespace()

    a = Integer(100, 200).set_tohu_name("a")
    b = Integer(300, 400).set_tohu_name("b")
    g = Apply(lambda x, y: x + y, a, b).set_tohu_name("g")

    assert len(ns) == 0

    # Add g, which should implicitly also add its input generators a and b
    ns.add_generator(g, "g")

    names_expected = ['ANONYMOUS_ANONYMOUS_ANONYMOUS_a', 'ANONYMOUS_ANONYMOUS_ANONYMOUS_b', 'g']
    assert len(ns) == 3
    assert names_expected == ns.keys()


def test_adding_generators_with_complex_dependencies():
    ns = TohuNamespace()

    mapping = {
        1: ['a', 'aa', 'aaa', 'aaaa', 'aaaaa'],
        2: ['b', 'bb', 'bbb', 'bbbb', 'bbbbb'],
        3: ['c', 'cc', 'ccc', 'cccc', 'ccccc'],
    }

    n_vals = Integer(1, 5)
    g = SelectMultiple(
        Lookup(
            g=Integer(1, 3).set_tohu_name("key_gen"),
            mapping=Constant(mapping).set_tohu_name("mapping")
        ).set_tohu_name("lookup"),
        num=n_vals.set_tohu_name("n_vals")
    )

    ns.add_generator(n_vals, name="aa")
    ns.add_generator(g, name="bb")

    names_expected = [
        "aa",
        "ANONYMOUS_ANONYMOUS_ANONYMOUS_key_gen",
        "ANONYMOUS_ANONYMOUS_ANONYMOUS_mapping",
        "ANONYMOUS_ANONYMOUS_ANONYMOUS_lookup",
        "bb"
    ]
    assert 5 == len(ns)
    assert names_expected == ns.keys()


def test_initialisation_from_dictionary():
    g1 = Integer(1, 5).set_tohu_name("g1")
    g2 = Constant(['a', 'b', 'c', 'd', 'e']).set_tohu_name("g2")
    g3 = SelectMultiple(values=g2, num=g1).set_tohu_name("g3")

    ns_dict = {"aa": g1, "bb": 12345, "cc": g3, "dd": "foobar"}
    ns = TohuNamespace.from_dict(ns_dict)

    expected_names = ["aa", "ANONYMOUS_ANONYMOUS_ANONYMOUS_g2", "cc"]
    assert 3 == len(ns)
    assert expected_names == ns.keys()


def test_resetting():
    g1 = Integer(1, 5).set_tohu_name("g1")
    g2 = Constant(['a', 'b', 'c', 'd', 'e']).set_tohu_name("g2")
    g3 = SelectMultiple(values=g2, num=g1).set_tohu_name("g3")

    ns = TohuNamespace()
    ns.add_generator(g1, name="aa")
    ns.add_generator(g3, name="bb")

    g1.reset = Mock(side_effect=g1.reset)
    g2.reset = Mock(side_effect=g2.reset)
    g3.reset = Mock(side_effect=g3.reset)

    ns.reset(seed=12345)
    g1.reset.assert_called_once_with(seed=831769172)
    g2.reset.assert_called_once_with(seed=2430986565)
    g3.reset.assert_called_once_with(seed=694443915)


def test_names_vs_keys():
    g1 = Integer(1, 5).set_tohu_name("g1")
    g2 = Constant(['a', 'b', 'c', 'd', 'e']).set_tohu_name("g2")
    g3 = SelectMultiple(values=g2, num=g1).set_tohu_name("g3")

    ns = TohuNamespace()
    ns.add_generator(g1, name="cc")
    ns.add_generator(g3, name="aa")

    assert ["cc", "aa"] == ns.names
    assert ["cc", "ANONYMOUS_ANONYMOUS_ANONYMOUS_g2", "aa"] == ns.keys()
