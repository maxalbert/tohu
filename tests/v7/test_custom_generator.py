from tohu.v7.primitive_generators import Integer, FakerGenerator, HashDigest
from tohu.v7.custom_generator import make_new_custom_generator


def test_make_custom_generator():
    g = make_new_custom_generator()
    assert g.fields == []
    assert g.field_generators == {}

    aa = Integer(1, 7)
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

    assert g.tohu_items_cls is None
    g.make_tohu_items_class("Quux")
    assert g.tohu_items_cls is not None
    assert g.tohu_items_cls.__name__ == "Quux"
    assert g.tohu_items_cls.field_names == ["aa", "bb", "cc"]
    assert repr(g.tohu_items_cls(aa=42, bb=True, cc="hello")) == "Quux(aa=42, bb=True, cc='hello')"


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
