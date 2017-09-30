"""
Tests for the ItemCollection class.
"""

import os
import pytest
import textwrap

from .context import tohu
from tohu.item_collection import ItemCollection
from tohu.custom_generator import CustomGenerator
from tohu.generators import ChooseFrom, HashDigest, Integer, Sequential, Timestamp


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

    def test_write_csv(self, tmpdir):
        filename = tmpdir.join("output.csv").strpath

        class FoobarGenerator(CustomGenerator):
            aaa = HashDigest(length=6)
            bbb = Sequential(prefix="Foo_", digits=2)
            ccc = Integer(0, 100)

        class QuuxGenerator(CustomGenerator):
            def __init__(self, foo_items):
                self.foo1 = ChooseFrom(foo_items)
                self.foo2 = ChooseFrom(foo_items)
                self.date_str = Timestamp(start="2006-01-01", end="2017-09-01", fmt='%d-%b-%y')

        foo = FoobarGenerator()
        foo_items = foo.generate(10, seed=12345)
        quux = QuuxGenerator(foo_items)
        quux_items = quux.generate(5, seed=99999)

        csv_fields = {
            'Column_1': 'foo1.aaa',
            'Column_2': 'foo1.bbb',
            'Column_3': 'foo2.aaa',
            'Column_4': 'foo2.ccc',
            'Column_5': 'date_str',
        }

        assert not os.path.exists(filename)
        quux_items.write(filename, fields=csv_fields)
        assert os.path.exists(filename)

        expected_output = textwrap.dedent("""\
            #Column_1,Column_2,Column_3,Column_4,Column_5
            27E995,Foo_04,27E995,58,25-Sep-10
            27E995,Foo_04,9CB45F,36,12-Aug-11
            9CB45F,Foo_10,297F9D,39,17-Jan-07
            1A2721,Foo_06,B2A827,1,05-Jan-16
            F5C771,Foo_08,8CE1AD,68,09-Mar-12
            """)

        assert open(filename).read() == expected_output