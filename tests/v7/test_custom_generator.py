import pytest
from tohu.v7.primitive_generators import Integer, FakerGenerator, HashDigest
from tohu.v7.custom_generator import make_new_custom_generator


def test_make_custom_generator():
    #
    # Create empty custom generator.
    #
    g = make_new_custom_generator()
    assert g.fields == []
    assert g.field_generators == {}

    #
    # Add field generators of different types.
    #
    aa = Integer(100, 200)
    g.add_field_generator("aa", aa)
    assert g.fields == ["aa"]
    assert g.field_generators["aa"].is_clone_of(aa)

    bb = HashDigest(length=8)
    g.add_field_generator("bb", bb)
    assert g.fields == ["aa", "bb"]
    assert g.field_generators["aa"].is_clone_of(aa)
    assert g.field_generators["bb"].is_clone_of(bb)

    cc = FakerGenerator(method="name")
    g.add_field_generator("cc", cc)
    assert g.fields == ["aa", "bb", "cc"]
    assert g.field_generators["aa"].is_clone_of(aa)
    assert g.field_generators["bb"].is_clone_of(bb)
    assert g.field_generators["cc"].is_clone_of(cc)

    #
    # Create tohu items classs and check that it can be
    # used to generate items with the correct fields.
    #
    assert g.tohu_items_cls.is_unset
    g.make_tohu_items_class("Quux")
    Quux = g.tohu_items_cls
    assert Quux.__name__ == "Quux"
    assert Quux.field_names == ["aa", "bb", "cc"]

    #
    # Check that the custom generator produces the expected items.
    #
    items_generated = g.generate(num=4, seed=99999)
    items_expected = [
        Quux(aa=104, bb="672EF2A4", cc="Calvin Peters"),
        Quux(aa=114, bb="2502048A", cc="Amanda Taylor"),
        Quux(aa=148, bb="679DAED2", cc="Amanda Barrett"),
        Quux(aa=126, bb="91554CC8", cc="Jesse Williams"),
    ]
    assert items_expected == items_generated


def test_must_create_items_class_before_generating_items():
    g = make_new_custom_generator()
    g.add_field_generator("aa", Integer(100, 200))

    with pytest.raises(
        RuntimeError, match="You must call `make_tohu_items_class` on the custom generator before generating items."
    ):
        g.generate(num=4, seed=99999)

    g.make_tohu_items_class("Quux")
    assert len(g.generate(num=6, seed=99999)) == 6


# def test_custom_generator():
#
#     class QuuxGenerator(CustomGenerator):
#         aa = Integer(1, 7)
#         bb = HashDigest(length=8)
#         cc = FakerGenerator(method="name")
#         dd = Integer(100, 200)
#
#     g = QuuxGenerator()
#     expected_values = []
#     assert expected_values == g.generate(num=5, seed=99999)
