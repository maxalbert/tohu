"""
Tests for the ItemList class.
"""

import os
import pandas as pd
import pytest
import textwrap

from .context import tohu
from tohu.item_list import ItemList
from tohu.custom_generator import CustomGenerator
from tohu.generators import SelectOne, Float, HashDigest, Integer, Sequential, Timestamp


class TestItemList:

    @pytest.mark.parametrize("items, N", [
        ([42, 23, "Hello", 12, "foobar"], 5),
        (range(100), 100),
    ])
    def test_converting_item_list_to_list_returns_original_items(self, items, N):
        """
        Converting an ItemList to a list returns the original items.
        """
        c = ItemList(items, N)
        assert list(c) == list(items)

    def test_length(self):
        c = ItemList(["hello", "world", "foobar", "quux"], 4)
        assert len(c) == 4

    def test_indexing(self):
        c = ItemList(["hello", "world", "foobar", "quux"], 4)
        assert c[0] == "hello"
        assert c[1] == "world"
        assert c[2] == "foobar"
        assert c[3] == "quux"

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
                self.foo1 = SelectOne(foo_items)
                self.foo2 = SelectOne(foo_items)
                self.date_str = Timestamp(start="2006-01-01", end="2017-09-01", fmt='%d-%b-%y')

        foo = FoobarGenerator()
        foo_items = foo.generate(10, seed=12345)
        quux = QuuxGenerator(foo_items)

        csv_fields = {
            'Column_1': 'foo1.aaa',
            'Column_2': 'foo1.bbb',
            'Column_3': 'foo2.aaa',
            'Column_4': 'foo2.ccc',
            'Column_5': 'date_str',
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
            B1DB13,Foo_03,4F7953,50,17-Apr-10
            4F7953,Foo_04,593213,66,18-Feb-08
            FD8AFB,Foo_09,855677,81,20-Jul-14
            0A76B2,Foo_06,FFB25A,90,10-Jun-15
            C6CD8C,Foo_10,855677,81,15-Sep-06
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

    def test_export_dataframe(self):
        """
        Test that to_df() produces the expected pandas dataframe.
        """
        class QuuxGenerator(CustomGenerator):
            c = Sequential(prefix="quux_", digits=2)
            d = Float(7., 8.)
            e = Integer(low=3000, high=6000)

        g = QuuxGenerator()
        items = g.generate(N=4, seed=12345)

        df_expected = pd.DataFrame({
            'c': ['quux_01', 'quux_02', 'quux_03', 'quux_04'],
            'd': [7.429949009333706, 7.137420914800083, 7.820307854938839, 7.145680371214801],
            'e': [5895, 5318, 4618, 5606],
        })

        df = items.to_df()
        pd.testing.assert_frame_equal(df_expected, df)
