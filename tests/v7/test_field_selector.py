import pytest
from tohu.v7.field_selector import FieldSelector
from tohu.v7.custom_generator import make_tohu_items_class


def test_field_selector():
    Quux = make_tohu_items_class("Quux", field_names=["cc", "aa", "bb"])
    input_items = [Quux(aa=104, bb="672EF2", cc="Johnny"), Quux(aa=114, bb="250204", cc="David")]

    fs = FieldSelector(Quux)
    items_expected = [{"aa": 104, "bb": "672EF2", "cc": "Johnny"}, {"aa": 114, "bb": "250204", "cc": "David"}]
    assert items_expected == list(fs(input_items))

    fs = FieldSelector(Quux, fields=["cc", "aa"])
    items_expected = [{"cc": "Johnny", "aa": 104}, {"cc": "David", "aa": 114}]
    assert items_expected == list(fs(input_items))

    fs = FieldSelector(Quux, fields={"id": "bb", "name": "cc"})
    items_expected = [{"id": "672EF2", "name": "Johnny"}, {"id": "250204", "name": "David"}]
    assert items_expected == list(fs(input_items))


@pytest.mark.skip(reason="Consistency checks of nested fields is not supported yet")
def test_field_selector_raises_error_if_fields_are_inconsistent():
    Quux = make_tohu_items_class("Quux", field_names=["aa", "bb", "cc"])

    with pytest.raises(ValueError, match="Field names must be a subset of the fields defined on `tohu_items_cls`"):
        FieldSelector(Quux, fields=["not_an_existing_field"])

    with pytest.raises(ValueError, match="Field names must be a subset of the fields defined on `tohu_items_cls`"):
        FieldSelector(Quux, fields={"new_field": "not_an_existing_field"})


def test_extraction_of_nested_fields():
    Foo = make_tohu_items_class("Foo", field_names=["my_name", "my_age"])
    foo_item = Foo("Peter", 42)

    Quux = make_tohu_items_class("Quux", field_names=["aa", "bb"])
    input_items = [Quux(aa="D8A024", bb=foo_item), Quux(aa="CC3ABB", bb=foo_item), Quux(aa="5398D1", bb=foo_item)]

    fs = FieldSelector(Quux, fields={"name": "bb.my_name", "age": "bb.my_age", "id": "aa"})
    items_expected = [
        {"name": "Peter", "age": 42, "id": "D8A024"},
        {"name": "Peter", "age": 42, "id": "CC3ABB"},
        {"name": "Peter", "age": 42, "id": "5398D1"},
    ]
    assert items_expected == list(fs(input_items))
