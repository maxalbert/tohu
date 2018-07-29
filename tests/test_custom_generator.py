"""
Tests for the CustomGenerator class.
"""

import pytest

import pandas as pd
import textwrap
from .context import tohu

from tohu.generators import Constant, Integer, Float, Sequential
from tohu.custom_generator import CustomGenerator


class TestCustomGenerator:

    def setup(self):

        class FoobarGenerator(CustomGenerator):
            a = Integer(low=1000, high=9000)
            b = Sequential(prefix="foo_", digits=3)

        class QuuxGenerator(CustomGenerator):
            c = Constant("Hello")
            d = Sequential(prefix="quux_", digits=2)
            e = Integer(low=3000, high=6000)

        self.gen_foo = FoobarGenerator().reset(seed=99999)
        self.gen_quux = QuuxGenerator().reset(seed=12345)

    def test_custom_generator_produces_objects_of_the_expected_class(self):
        """
        Test that generators FoobarGenerator and QuuxGenerator produce items
        that are instances of a classes named Foobar and Quux, respectively.
        """

        item1 = next(self.gen_foo)
        item2 = next(self.gen_quux)

        assert item1.__class__.__name__ == "Foobar"
        assert item2.__class__.__name__ == "Quux"

    def test_custom_generator_produces_namedtuples_with_expected_field_values(self):
        """
        Test that FoobarGenerator and QuuxGenerator produce namedtuples with fields
        produced by their respective generators.
        """

        item1 = next(self.gen_foo)
        item2 = next(self.gen_foo)

        item3 = next(self.gen_quux)
        item4 = next(self.gen_quux)

        assert item1 == (7715, "foo_001")
        assert item2 == (2325, "foo_002")

        assert item3 == ("Hello", "quux_01", 5895)
        assert item4 == ("Hello", "quux_02", 5318)

    def test_fields_can_be_defined_at_classlevel_and_in_init(self):
        """
        Test that fields can be defined at classlevel an in __init__() of custom generators.
        """
        class QuuxGenerator(CustomGenerator):
            x = Integer(low=400, high=499)

            def __init__(self, z_min, z_max):
                self.y = Float(low=z_min, high=z_max)

        g1 = QuuxGenerator(z_min=2.0, z_max=3.0)
        g2 = QuuxGenerator(z_min=5.0, z_max=6.0)
        g1.reset(seed=12345)
        g2.reset(seed=12345)

        item1 = next(g1)
        item2 = next(g2)

        assert str(item1) == "Quux(x=402, y=2.4299490093337055)"
        assert str(item2) == "Quux(x=402, y=5.429949009333706)"

    @pytest.mark.skip(msg="Formatting needs to be reworked and it's unclear what format(item) should return")
    def test_formatting_items_returns_string_with_field_values(self):
        """
        Test that formatting items produced by {Foobar|Quux}Generator
        results in strings that are concatenations of their field values.
        """

        item1 = next(self.gen_foo)
        item2 = next(self.gen_foo)

        item3 = next(self.gen_quux)
        item4 = next(self.gen_quux)

        assert str(item1) == "Foobar(a=2184, b='foo_001')"
        assert str(item2) == "Foobar(a=8875, b='foo_002')"
        assert format(item1) == "2184,foo_001"
        assert format(item2) == "8875,foo_002"

        assert str(item3) == "Quux(c='Hello', d='quux_01', e=4001)"
        assert str(item4) == "Quux(c='Hello', d='quux_02', e=5032)"
        assert format(item3) == "Hello,quux_01,4001"
        assert format(item4) == "Hello,quux_02,5032"

    @pytest.mark.xfail(reason="This should be moved out into tests for ItemList")
    def test_return_csv_string(self):
        """
        Test that to_csv() returns the expected CSV string if no filename is given.
        """
        csv_expected = textwrap.dedent("""\
            # Custom header
            1181,foo_001
            5144,foo_002
            7732,foo_003
            """)

        csv = self.gen_foo.to_csv(N=3, seed=12345, header="# Custom header")
        assert csv == csv_expected

    @pytest.mark.xfail(reason="This should be moved out into tests for ItemList")
    def test_write_csv_file(self, tmpdir):
        """
        Test that generated items can be written to a CSV file.
        """
        filename1 = tmpdir.join("output1.txt").strpath
        filename2 = tmpdir.join("output2.txt").strpath

        self.gen_foo.to_csv(filename1, N=3, seed=12345, header="# Custom header")
        self.gen_foo.to_csv(filename2, N=3, seed=12345, header="# Custom header")

        csv_expected = textwrap.dedent("""\
            # Custom header
            1181,foo_001
            5144,foo_002
            7732,foo_003
            """)

        assert open(filename1).read() == csv_expected
        assert open(filename2).read() == csv_expected

    @pytest.mark.xfail(reason="Need to re-think whether the CSV_FIELDS attribute is a good idea")
    def test_csv_fields_can_be_defined_in_class_declaration(self, tmpdir):
        """
        Test that fields for CSV export can be defined via the CSV_FIELDS class attribute.
        """
        class FoobarGenerator(CustomGenerator):
            a = Integer(low=1000, high=9000)
            b = Sequential(prefix="foo_", digits=3)
            CSV_FIELDS = {"Column 1": "a=${a}", "Column 2": "b=${b}"}

        filename = tmpdir.join("output.csv").strpath

        g = FoobarGenerator()
        g.to_csv(filename, N=3, seed=12345)

        csv_expected = textwrap.dedent("""\
            #Column 1,Column 2
            a=1181,b=foo_001
            a=5144,b=foo_002
            a=7732,b=foo_003
            """)

        assert open(filename).read() == csv_expected

    @pytest.mark.xfail(reason="Need to re-think whether the CSV_FIELDS and CSV_HEADER attributes are a good idea")
    def test_csv_header_can_be_defined_in_class_declaration(self, tmpdir):
        """
        Test that CSV header can be defined via the CSV_HEADER class attribute .
        """
        class FoobarGenerator(CustomGenerator):
            a = Integer(low=1000, high=9000)
            b = Sequential(prefix="foo_", digits=3)
            CSV_HEADER = "# My custom header line"
            CSV_FIELDS = {"Column 1": "a: ${a}", "Column 2": "b: ${b}"}

        filename = tmpdir.join("output.csv").strpath

        g = FoobarGenerator()
        g.to_csv(filename, N=3, seed=12345)

        csv_expected = textwrap.dedent("""\
            # My custom header line
            a: 1181,b: foo_001
            a: 5144,b: foo_002
            a: 7732,b: foo_003
             """)

        assert open(filename).read() == csv_expected

    @pytest.mark.xfail(reason="Need to re-think whether the CSV_FMT_STR attribute is a good idea")
    def test_csv_format_string_can_be_defined_in_class_declaration(self, tmpdir):
        """
        Test that CSV formatting can be defined via the CSV_FMT_STR class attribute .
        """
        class FoobarGenerator(CustomGenerator):
            a = Integer(low=1000, high=9000)
            b = Sequential(prefix="foo_", digits=3)
            CSV_FMT_STR = "a=${a} || b: ${b}"

        filename = tmpdir.join("output.csv").strpath

        g = FoobarGenerator()
        g.to_csv(filename, N=3, seed=12345)

        csv_expected = textwrap.dedent("""\
            a=1181 || b: foo_001
            a=5144 || b: foo_002
            a=7732 || b: foo_003
            """)

        assert open(filename).read() == csv_expected

    @pytest.mark.xfail(reason="The .to_df() method has been disabled (and will likely be removed)")
    def test_dataframe_export(self):
        """
        Test that items produced by generator can be exported as a pandas dataframe.
        """
        class QuuxGenerator(CustomGenerator):
            c = Sequential(prefix="quux_", digits=2)
            d = Float(7., 8.)
            e = Integer(low=3000, high=6000)

        g = QuuxGenerator()
        df = g.to_df(N=4, seed=12345)

        df_expected = pd.DataFrame({
            'c': ['quux_01', 'quux_02', 'quux_03', 'quux_04'],
            'd': [7.429949009333706, 7.137420914800083, 7.820307854938839, 7.145680371214801],
            'e': [5895, 5318, 4618, 5606],
        })

        pd.testing.assert_frame_equal(df_expected, df)
