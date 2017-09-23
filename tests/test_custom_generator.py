"""
Tests for the CustomGenerator class.
"""

import pytest
from .context import tohu

from tohu.generators import Constant, Integer, Sequential
from tohu.custom_generator import CustomGenerator


class TestCustomGenerator:

    def setup(self):

        class FoobarGenerator(CustomGenerator):
            a = Integer(lo=1000, hi=2000)
            b = Sequential(prefix="foo_", digits=3)

        class QuuxGenerator(CustomGenerator):
            c = Constant("Hello")
            d = Sequential(prefix="quux_", digits=2)
            e = Integer(lo=3000, hi=4000)

        self.gen_foo = FoobarGenerator(seed=12345)
        self.gen_quux = QuuxGenerator(seed=99999)

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

        assert item1 == (1426, "foo_001")
        assert item2 == (1750, "foo_002")

        assert item3 == ("Hello", "quux_01", 3123)
        assert item4 == ("Hello", "quux_02", 3972)

    def test_formatting_items_returns_string_with_field_values(self):
        """
        Test that formatting items produced by {Foobar|Quux}Generator
        results in strings that are concatenations of their field values.
        """

        item1 = next(self.gen_foo)
        item2 = next(self.gen_foo)

        item3 = next(self.gen_quux)
        item4 = next(self.gen_quux)

        assert str(item1) == "Foobar(a=1426, b='foo_001')"
        assert str(item2) == "Foobar(a=1750, b='foo_002')"
        assert format(item1) == "1426,foo_001\n"
        assert format(item2) == "1750,foo_002\n"

        assert str(item3) == "Quux(c='Hello', d='quux_01', e=3123)"
        assert str(item4) == "Quux(c='Hello', d='quux_02', e=3972)"
        assert format(item3) == "Hello,quux_01,3123\n"
        assert format(item4) == "Hello,quux_02,3972\n"

    def test_format_attribute_is_taken_into_account(self):
        """
        Test that if the attributes FMT_FIELDS or SEPARATOR are defined,
        these are taken into account when formatting items.
        """

        self.gen_foo.FMT_FIELDS = {"Field b": "b has value: ${b}"}

        self.gen_quux.FMT_FIELDS = {"Field e": "e=${e}", "Field d": "d has value: ${d}"}  # note the reversed order
        self.gen_quux.SEPARATOR = " | "

        item1 = next(self.gen_foo)
        item2 = next(self.gen_foo)
        item3 = next(self.gen_quux)
        item4 = next(self.gen_quux)

        # String formatting is the same as before (not affected by the FMT_FIELDS attribute)
        assert str(item1) == "Foobar(a=1426, b='foo_001')"
        assert str(item2) == "Foobar(a=1750, b='foo_002')"
        assert str(item3) == "Quux(c='Hello', d='quux_01', e=3123)"
        assert str(item4) == "Quux(c='Hello', d='quux_02', e=3972)"

        # By contrast, format() uses the FMT_FIELDS and SEPARATOR attributes
        assert format(item1) == "b has value: foo_001\n"
        assert format(item2) == "b has value: foo_002\n"
        assert format(item3) == "e=3123 | d has value: quux_01\n"
        assert format(item4) == "e=3972 | d has value: quux_02\n"
