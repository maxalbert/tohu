from random import Random

from .base import TohuBaseGenerator, SeedGenerator
from .primitive_generators import as_tohu_generator
from .spawn_mapping import SpawnMapping

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
        for gen in self.constituent_generators:
            gen.owner = self

    def __next__(self):
        args = [next(g) for g in self.arg_gens]
        kwargs = {name: next(g) for name, g in self.kwarg_gens.items()}
        return self.callable(*args, **kwargs)

    def reset(self, seed):
        super().reset(seed)

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_arg_gens = [spawn_mapping[g] for g in self.arg_gens]
        new_kwarg_gens = {name: spawn_mapping[g] for name, g in self.kwarg_gens}
        new_obj = Apply(self.callable, *new_arg_gens, **new_kwarg_gens)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        for g_self, g_other in zip(self.constituent_generators, other.constituent_generators):
            g_self._set_random_state_from(g_other)


class Lookup(Apply):

    def __init__(self, key, mapping):
        self.key = as_tohu_generator(key)
        self.mapping = as_tohu_generator(mapping)

        def f_lookup(key, mapping):
            return mapping[key]

        super().__init__(f_lookup, self.key, self.mapping)

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_obj = Lookup(spawn_mapping[self.key], spawn_mapping[self.mapping])
        new_obj._set_random_state_from(self)
        return new_obj


class SelectMultiple(Apply):

    def __init__(self, values, num):
        self.values_gen = as_tohu_generator(values)
        self.num_gen = as_tohu_generator(num)
        self.randgen = Random()
        func = self.randgen.choices
        super().__init__(func, self.values_gen, k=self.num_gen)

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_obj = SelectMultiple(spawn_mapping[self.values_gen], spawn_mapping[self.num_gen])
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())
