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

    @pytest.mark.parametrize("items, N", [
        ([42, 23, "Hello", 12, "foobar"], 5),
        (range(100), 100),
    ])
    def test_converting_item_collection_to_list_returns_original_items(self, items, N):
        """
        Converting an ItemCollection to a list returns the original items.
        """
        c = ItemCollection(items, N)
        assert list(c) == list(items)

    def test_length(self):
        c = ItemCollection(["hello", "world", "foobar", "quux"], 4)
        assert len(c) == 4

    def test_write_csv(self, tmpdir):
        filename1 = tmpdir.join("output_without_header.csv").strpath
        filename2 = tmpdir.join("output_with_default_header.csv").strpath
        filename3 = tmpdir.join("output_with_custom_header.csv").strpath

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
        foo_items = list(foo.generate(10, seed=12345))
        quux = QuuxGenerator(foo_items)

        csv_fields = {
            'Column_1': '${foo1.aaa}',
            'Column_2': '${foo1.bbb}',
            'Column_3': '${foo2.aaa}',
            'Column_4': '${foo2.ccc}',
            'Column_5': '${date_str}',
        }

        assert not os.path.exists(filename1)
        assert not os.path.exists(filename2)
        assert not os.path.exists(filename3)
        quux_items = quux.generate(5, seed=99999)
        quux_items.to_csv(filename1, fields=csv_fields, header=False)
        quux_items = quux.generate(5, seed=99999)
        quux_items.to_csv(filename2, fields=csv_fields, header=True)
        quux_items = quux.generate(5, seed=99999)
        quux_items.to_csv(filename3, fields=csv_fields, header="# This is a custom header line")
        assert os.path.exists(filename1)
        assert os.path.exists(filename2)
        assert os.path.exists(filename3)

        expected_output_without_header = textwrap.dedent("""\
            27E995,Foo_04,27E995,58,25-Sep-10
            27E995,Foo_04,9CB45F,36,12-Aug-11
            9CB45F,Foo_10,297F9D,39,17-Jan-07
            1A2721,Foo_06,B2A827,1,05-Jan-16
            F5C771,Foo_08,8CE1AD,68,09-Mar-12
            """)

        expected_output_with_default_header = \
            ("#Column_1,Column_2,Column_3,Column_4,Column_5\n" +
             expected_output_without_header)

        expected_output_with_custom_header = \
            ("# This is a custom header line\n" +
             expected_output_without_header)

        assert open(filename1).read() == expected_output_without_header
        assert open(filename2).read() == expected_output_with_default_header
        assert open(filename3).read() == expected_output_with_custom_header