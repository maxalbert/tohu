from random import Random

from .base import TohuBaseGenerator, SeedGenerator
from .primitive_generators import as_tohu_generator

__all__ = ['Apply', 'Lookup', 'SelectMultiple']


class DerivedGenerator(TohuBaseGenerator):
    """
    Base class for all derived generators
    """

    def reset_input_generators(self, seed):
        """
        Helper method which explicitly resets all input generators
        to the derived generator. This should only ever be called
        for testing or debugging.
        """
        seed_generator = SeedGenerator().reset(seed=seed)

        for gen in self.input_generators:
            gen.reset(next(seed_generator))


class Apply(DerivedGenerator):

    def __init__(self, callable, *arg_gens, **kwarg_gens):
        super().__init__()
        self.callable = callable
        self.arg_gens_orig = arg_gens
        self.kwarg_gens_orig = kwarg_gens

        self.arg_gens = [g.clone() for g in self.arg_gens_orig]
        self.kwarg_gens = {name: g.clone() for name, g in self.kwarg_gens_orig.items()}
        self.input_generators = [g for g in self.arg_gens_orig] + [g for g in self.kwarg_gens_orig.values()]
        self.constituent_generators = [g for g in self.arg_gens] + [g for g in self.kwarg_gens.values()]

    def __next__(self):
        args = [next(g) for g in self.arg_gens]
        kwargs = {name: next(g) for name, g in self.kwarg_gens.items()}
        return self.callable(*args, **kwargs)

    def reset(self, seed):
        super().reset(seed)

    def spawn(self):
        return Apply(self.callable, *self.arg_gens, **self.kwarg_gens)


class Lookup(Apply):

    def __init__(self, g, mapping):
        self.g = g
        self.mapping = mapping

        def f_lookup(key):
            return mapping[key]

        super().__init__(f_lookup, g)

    def spawn(self):
        return Lookup(self.g, self.mapping)


class SelectMultiple(Apply):

    def __init__(self, parent, num):
        parent = as_tohu_generator(parent)
        num = as_tohu_generator(num)

        self.parent = parent
        self.num = num
        self.randgen = Random()
        func = self.randgen.choices
        super().__init__(func, parent, k=self.num)

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)

    def spawn(self):
        return SelectMultiple(self.parent, self.num)

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())
