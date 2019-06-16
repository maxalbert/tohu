import pytest

from .context import tohu
from tohu.v7.base import TohuBaseGenerator
from tohu.v7.primitive_generators import Integer
from tohu.v7.foreach import foreach, Placeholder, placeholder


def test_foreach():
    cc_outside = "<cc_is_defined_outside_the_class>"

    @foreach(upper_bound=Placeholder("upper_bound"), foobar=placeholder)
    class AA(TohuBaseGenerator):
        aa = Integer(low=100, high=upper_bound)
        cc = cc_outside  # TODO: ensure that variables defined outside the class are available in the rewritten class

        def __init__(self, bb):
            super().__init__()
            self.bb = bb
            self.foobar = foobar

        def __next__(self):
            return (next(self.aa), self.bb)

        def reset(self, seed):
            super().reset(seed)
            self.aa.reset(next(self.seed_generator))

        def spawn(self):
            pass

        def _set_state_from(self, other):
            pass

    g = AA(bb=232323)
    h = g.foreach(upper_bound=424242, foobar="this works!")

    # TODO: what names do we want for the classes of g and h?
    # Hmm, probably both should be named `AA`, but in the repr we want to indicate
    # that g is a "foreach closure/wrapper" around AA whereas h is the actual object
    # that we would call an instance of AA.
    assert g.__class__.__name__ == "ForeachWrapper"
    assert h.__class__.__name__ == "AA"

    assert h.aa.high == 424242
    assert h.bb == 232323
    assert h.foobar == "this works!"
    assert h.cc == "<cc_is_defined_outside_the_class>"

    items_expected = [(16640, 232323), (59838, 232323), (199249, 232323), (108034, 232323), (318445, 232323)]
    assert items_expected == list(h.generate(num=5, seed=99999))

    g = AA(bb=112233)
    h = g.foreach(upper_bound=200, foobar="this works too!")

    assert h.aa.high == 200
    assert h.bb == 112233
    assert h.foobar == "this works too!"
    assert h.cc == "<cc_is_defined_outside_the_class>"

    items_expected = [(104, 112233), (114, 112233), (148, 112233), (126, 112233), (177, 112233)]
    assert items_expected == list(h.generate(num=5, seed=99999))


def test_error_if_not_applied_to_tohu_generator_class():
    with pytest.raises(TypeError, match="Foreach decorator must be applied to a tohu generator class"):

        @foreach(foo=[1, 2, 3])
        def some_function():
            pass

    with pytest.raises(TypeError, match="Decorated class must be a subclass of TohuBaseGenerator."):

        @foreach(foo=[1, 2, 3])
        class SomeClass:
            pass
