import pytest
from .context import tohu
from tohu.v7.custom_generator import make_tohu_items_class


def test_make_tohu_items_class():
    quux_cls = make_tohu_items_class("Quux", field_names=["foo", "bar", "baz"])
    assert quux_cls.field_names == ["foo", "bar", "baz"]

    item1 = quux_cls(42, True, "hello")
    item2 = quux_cls(baz="hello", foo=42, bar=True)
    item3 = quux_cls(baz="hi", foo=23, bar=False)

    assert "Quux(foo=42, bar=True, baz='hello')" == repr(item1)
    assert "Quux(foo=42, bar=True, baz='hello')" == repr(item2)
    assert "Quux(foo=23, bar=False, baz='hi')" == repr(item3)

    assert {"foo": 42, "bar": True, "baz": "hello"} == item1.as_dict() == item2.as_dict()

    assert item1 == item2
    assert item1 == (42, True, "hello")
    assert item1 == {"baz": "hello", "bar": True, "foo": 42}
    assert item1 != item3



def test_comparison_between_incompatible_tohu_item_classes():
    quux_cls = make_tohu_items_class("Quux", field_names=["foo", "bar", "baz"])
    quux_cls_newly_defined = make_tohu_items_class("Quux", field_names=["foo", "bar", "baz"])
    quux2_cls = make_tohu_items_class("Quux2", field_names=["aa", "bb"])

    item1 = quux_cls(foo=42, bar=True, baz="hello")
    item2 = quux_cls_newly_defined(foo=42, bar=True, baz="hello")
    item3 = quux2_cls(aa=12, bb=14)

    with pytest.raises(TypeError, match="Tohu items have types that cannot be compared"):
        item1 == item2

    with pytest.raises(TypeError, match="Tohu items have types that cannot be compared"):
        item1 == item3