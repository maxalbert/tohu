import pytest
from tohu.v7.primitive_generators import Integer, FakerGenerator, HashDigest
from tohu.v7.custom_generator import CustomGenerator


def test_make_custom_generator():
    #
    # Create empty custom generator.
    #
    g = CustomGenerator()
    g.set_tohu_items_class_name("Quux")
    assert g.field_names == []
    assert g.field_generators == {}

    #
    # Add field generators of different types.
    #
    aa = Integer(100, 200)
    g.add_field_generator("aa", aa)
    assert g.field_names == ["aa"]
    assert g.field_generators["aa"].is_clone_of(aa)
    assert g.tohu_items_cls.__name__ == "Quux"
    assert g.tohu_items_cls.field_names == ["aa"]

    bb = HashDigest(length=8)
    g.add_field_generator("bb", bb)
    assert g.field_names == ["aa", "bb"]
    assert g.field_generators["aa"].is_clone_of(aa)
    assert g.field_generators["bb"].is_clone_of(bb)
    assert g.tohu_items_cls.__name__ == "Quux"
    assert g.tohu_items_cls.field_names == ["aa", "bb"]

    cc = FakerGenerator(method="name")
    g.add_field_generator("cc", cc)
    assert g.field_names == ["aa", "bb", "cc"]
    assert g.field_generators["aa"].is_clone_of(aa)
    assert g.field_generators["bb"].is_clone_of(bb)
    assert g.field_generators["cc"].is_clone_of(cc)
    assert g.tohu_items_cls.__name__ == "Quux"
    assert g.tohu_items_cls.field_names == ["aa", "bb", "cc"]

    #
    # Check that the custom generator produces the expected items.
    #
    Quux = g.tohu_items_cls
    items_generated = g.generate(num=4, seed=99999)
    items_expected = [
        Quux(aa=104, bb="672EF2A4", cc="Calvin Peters"),
        Quux(aa=114, bb="2502048A", cc="Amanda Taylor"),
        Quux(aa=148, bb="679DAED2", cc="Amanda Barrett"),
        Quux(aa=126, bb="91554CC8", cc="Jesse Williams"),
    ]
    assert items_expected == items_generated


def test_must_set_items_class_name_before_adding_field_generators():
    g = CustomGenerator()

    msg_expected = "You must call `set_tohu_items_class_name` on the custom generator before adding field generators."
    with pytest.raises(RuntimeError, match=msg_expected):
        g.add_field_generator("aa", Integer(100, 200))

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
