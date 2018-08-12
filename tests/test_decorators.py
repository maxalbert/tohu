import pytest

from .context import tohu
from tohu.decorators import foreach, with_context
from tohu import CustomGenerator, HashDigest, Integer, IterateOver


def test_define_additional_variable_in_context_decorator():
    """
    Test that @with_context allows defining additional variables
    """
    predefined_values = {'some_value': 'quux'}

    @with_context(vals=predefined_values)
    class Foo:
        a = 42
        b = 'foo'
        c = vals['some_value']

    foo = Foo()
    assert foo.c == 'quux'


def test_multiple_context_decorators_dont_interfere():
    """
    Test that multiple instances of @with_context don't interfere
    """
    predefined_values_1 = {'some_value': 'quux_1'}
    predefined_values_2 = {'some_value': 'quux_2'}

    @with_context(vals=predefined_values_1)
    class Foo:
        x = vals['some_value']

    @with_context(vals=predefined_values_2)
    class Bar:
        x = vals['some_value']

    foo = Foo()
    bar = Bar()
    assert foo.x == 'quux_1'
    assert bar.x == 'quux_2'


@pytest.mark.xfail(reason='This needs some more magic to dynamically update the namespace in which __init__ executes')
def test_that_extra_variables_are_visible_in_init():
    """
    Extra variables are visible in __init__()
    """
    predefined_values = {'some_value': 'quux'}

    @with_context(vals=predefined_values)
    class Foo:
        def __init__(self):
            self.new_val = vals['some_value']

    foo = Foo()
    assert foo.new_val == 'quux'


@pytest.mark.parametrize("input_iterable", [
    IterateOver(['pp_01', 'pp_02', 'pp_03']),
    ['pp_01', 'pp_02', 'pp_03'],
    ('pp_01', 'pp_02', 'pp_03')])
def test_foreach_decorator(input_iterable):
    """
    Foreach decorator iterates over each element in the given input
    """

    @foreach(pp=input_iterable)
    class QuuxGenerator(CustomGenerator):
        aa = HashDigest(length=8)
        bb = pp

    g = QuuxGenerator()
    g.reset(seed=12345)
    items = [x for x in g]

    Quux = QuuxGenerator.item_cls
    items_expected = [
        Quux(aa='046CE0FF', bb='pp_01'),
        Quux(aa='B25AB1DB', bb='pp_02'),
        Quux(aa='134F7953', bb='pp_03'),
    ]

    assert items == items_expected