import pandas as pd
from pandas.util.testing import assert_frame_equal

from .context import tohu
from tohu.v7.item_list import ItemList
from tohu.v7.custom_generator import make_tohu_items_class


def test_item_list():
    values = [11, 55, 22, 66, 33]
    item_list = ItemList(values)
    assert item_list.items == values
    assert item_list == values
    assert len(item_list) == 5
    assert item_list[3] == 66
    assert [x for x in item_list] == values

    item_list_2 = ItemList(values)
    assert item_list == item_list_2

    item_list_3 = ItemList([1, 5, 8, 3])
    assert item_list != item_list_3


def test_to_df():
    Quux = make_tohu_items_class("Quux", field_names=["foo", "bar", "baz"])
    item1 = Quux(42, True, "hello")
    item2 = Quux(23, False, "world")
    item_list = ItemList([item1, item2], tohu_items_cls=Quux)

    df = item_list.to_df()
    df_expected = pd.DataFrame({"foo": [42, 23], "bar": [True, False], "baz": ["hello", "world"]})
    assert_frame_equal(df, df_expected)


def test_to_df_with_selected_fields_and_column_renaming():
    Quux = make_tohu_items_class("Quux", field_names=["foo", "bar", "baz"])
    items = [Quux(42, True, "hello"), Quux(23, False, "world")]
    item_list = ItemList(items, tohu_items_cls=Quux)

    df = item_list.to_df(fields=["baz", "foo"])
    df_expected = pd.DataFrame({"baz": ["hello", "world"], "foo": [42, 23]})
    assert_frame_equal(df, df_expected)

    df = item_list.to_df(fields={"xx": "bar", "yy": "foo"})
    df_expected = pd.DataFrame({"xx": [True, False], "yy": [42, 23]})
    assert_frame_equal(df, df_expected)
