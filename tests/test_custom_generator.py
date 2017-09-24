"""
Tests for the CustomGenerator class.
"""

import pytest
import textwrap
from .context import tohu

from tohu.generators import Constant, Integer, Float, Sequential
from tohu.custom_generator import CustomGenerator


class TestCustomGenerator:

    def setup(self):

        class FoobarGenerator(CustomGenerator):
            a = Integer(lo=1000, hi=9000)
            b = Sequential(prefix="foo_", digits=3)

        class QuuxGenerator(CustomGenerator):
            c = Constant("Hello")
            d = Sequential(prefix="quux_", digits=2)
            e = Integer(lo=3000, hi=6000)

        self.gen_foo = FoobarGenerator(seed=99999)
        self.gen_quux = QuuxGenerator(seed=12345)

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

        assert item1 == (2184, "foo_001")
        assert item2 == (8875, "foo_002")

        assert item3 == ("Hello", "quux_01", 4001)
        assert item4 == ("Hello", "quux_02", 5032)

    def test_fields_can_be_defined_at_classlevel_and_in_init(self):
        """
        Test that fields can be defined at classlevel an in __init__() of custom generators.
        """
        class QuuxGenerator(CustomGenerator):
            x = Integer(lo=400, hi=499)

            def __init__(self, z_min, z_max):
                self.y = Float(lo=z_min, hi=z_max)

        g1 = QuuxGenerator(z_min=2.0, z_max=3.0)
        g2 = QuuxGenerator(z_min=5.0, z_max=6.0)
        g1.reset(seed=12345)
        g2.reset(seed=12345)

        item1 = next(g1)
        item2 = next(g2)

        assert str(item1) == "Quux(x=488, y=2.032576355272894)"
        assert str(item2) == "Quux(x=496, y=5.032576355272894)"

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
