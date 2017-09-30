"""
Tests for the ItemCollection class.
"""

import pytest
from .context import tohu
from tohu.item_collection import ItemCollection


class TestItemCollection:

    @pytest.mark.parametrize("items", [[42, 23, "Hello", 12, "foobar"], range(100)])
    def test_converting_item_collection_to_list_returns_original_items(self, items):
        """
        Converting an ItemCollection to a list returns the original items.
        """
        c = ItemCollection(items)
        assert list(c) == list(items)

    def test_length(self):
        c = ItemCollection(["hello", "world", "foobar", "quux"])
        assert len(c) == 4

    def test_indexing(self):
        c = ItemCollection(["hello", "world", "foobar", "quux"])
        assert c[0] == "hello"
        assert c[1] == "world"
        assert c[2] == "foobar"
        assert c[3] == "quux"
