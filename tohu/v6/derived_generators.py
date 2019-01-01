from random import Random

from .base import TohuBaseGenerator, SeedGenerator
from .logging import logger
from .primitive_generators import as_tohu_generator
from .derived_timestamp_generator import TimestampDerived
from .spawn_mapping import SpawnMapping

__all__ = ['Apply', 'IntegerDerived', 'Lookup', 'SelectMultiple', 'SelectOne', 'Tee', 'TimestampDerived']


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
    """
    Generator which applies a callable to a elements produced by a set of input generators.
    """

    def __init__(self, callable, *arg_gens, max_value=None, **kwarg_gens):
        super().__init__()
        self.callable = callable
        self.arg_gens_orig = arg_gens
        self.kwarg_gens_orig = kwarg_gens
        self.max_value = max_value

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

        try:
            self.callable.reset(next(self.seed_generator))
        except AttributeError:
            logger.debug(
                f"Failed to reset callable in generator {self}. Assuming that"
                "it does not contain any random generators that need resetting."
            )

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_arg_gens_orig = [spawn_mapping[g] for g in self.arg_gens_orig]
        new_kwarg_gens_orig = {name: spawn_mapping[g] for name, g in self.kwarg_gens_orig}
        new_obj = Apply(self.callable, *new_arg_gens_orig, max_value=self.max_value, **new_kwarg_gens_orig)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        for g_self, g_other in zip(self.constituent_generators, other.constituent_generators):
            g_self._set_random_state_from(g_other)


class Lookup(Apply):
    """
    Generator which performs a lookup of elements produced by another generator.
    """

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


class IntegerDerived(Apply):

    def __init__(self, low, high):
        self.low_gen = as_tohu_generator(low)
        self.high_gen = as_tohu_generator(high)
        self.randgen = Random()
        super().__init__(self.randgen.randint, self.low_gen, self.high_gen)
        self.max_value = self.high_gen.max_value

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(next(self.seed_generator))

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_obj = IntegerDerived(spawn_mapping[self.low_gen], spawn_mapping[self.high_gen])
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())


class SelectOne(Apply):
    """
    Generator which selects a single element from each sequence produced by another generator.
    """

    def __init__(self, values):
        self.values_gen = as_tohu_generator(values)
        self.randgen = Random()
        func = self.randgen.choice
        super().__init__(func, self.values_gen)

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_obj = SelectOne(spawn_mapping[self.values_gen])
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())



class SelectMultiple(Apply):
    """
    Generator which selects multiple elements (without replacement)
    from each sequence produced by another generator.
    """

    def __init__(self, values, num):
        self.values_gen = as_tohu_generator(values)
        self.num_gen = as_tohu_generator(num)
        self.randgen = Random()
        func = self.randgen.sample
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

    def size(self):
        def get_size(x):
            return len(x)
        g = Apply(get_size, self, max_value=self.num_gen.max_value)
        return g


class Tee(Apply):

    def __init__(self, g, num):
        self.g_orig = g
        self.num_gen = as_tohu_generator(num)

        if self.num_gen.max_value > 1000:
            raise NotImplementedError(
                "This Tee generator is intended to be used to produce small-ish output tuples. "
                "The current implementation is not ideal for potentially large tuples, which"
                "which is why we only allow sizes up to 1000 elements at the moment."
            )

        def make_tuple(num, *values):
            return tuple(values[:num])

        value_gens = [g.spawn() for _ in range(self.num_gen.max_value)]
        super().__init__(make_tuple, self.num_gen, *value_gens)
