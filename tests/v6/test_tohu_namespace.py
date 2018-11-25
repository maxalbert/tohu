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

    ns.add_generator(g1, name="aa")
    ns.add_generator(g2, name="bb")

    assert ns["aa"] is g1
    assert ns["bb"] is g2
