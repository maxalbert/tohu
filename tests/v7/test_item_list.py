from .context import tohu
from tohu.v7.item_list import ItemList


def test_item_list():
    values = [11, 55, 22, 66, 33]
    item_list = ItemList(values)
    assert item_list.items == values
    assert item_list == values
    assert len(item_list) == 5
    assert item_list[3] == 66
    assert [x for x in item_list] == values
