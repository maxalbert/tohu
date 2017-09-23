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

        assert "Foobar(a=1426, b='foo_001')" == str(item1)
        assert "Foobar(a=1750, b='foo_002')" == str(item2)
        assert "1426,foo_001\n" == format(item1)
        assert "1750,foo_002\n" == format(item2)

        assert "Quux(c='Hello', d='quux_01', e=3123)" == str(item3)
        assert "Quux(c='Hello', d='quux_02', e=3972)" == str(item4)
        assert "Hello,quux_01,3123\n" == format(item3)
        assert "Hello,quux_02,3972\n" == format(item4)