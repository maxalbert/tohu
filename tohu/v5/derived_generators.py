from random import Random
from .base import TohuBaseGenerator, SpawnMapping
from .extras import as_tohu_generator

__all__ = ['Apply', 'DerivedGenerator', 'Lookup', 'SelectOneDerived']


class DerivedGenerator(TohuBaseGenerator):
    """
    Base class for all derived generators
    """


class Apply(DerivedGenerator):

    def __init__(self, callable, *arg_gens, spawn_mapping=None, **kwarg_gens):
        super().__init__()
        spawn_mapping = spawn_mapping or SpawnMapping()
        self.callable = callable
        self.arg_gens_orig = [spawn_mapping.get_spawn_or_orig(g) for g in arg_gens]
        self.kwarg_gens_orig = {name: spawn_mapping.get_spawn_or_orig(g) for name, g in kwarg_gens.items()}

        self.arg_gens = [g.clone(spawn_mapping) for g in self.arg_gens_orig]
        self.kwarg_gens = {name: g.clone(spawn_mapping) for name, g in self.kwarg_gens_orig.items()}
        self._input_generators = [g for g in self.arg_gens_orig] + [g for g in self.kwarg_gens_orig.values()]
        self._constituent_generators = [g for g in self.arg_gens] + [g for g in self.kwarg_gens.values()]

    def __next__(self):
        args = [next(g) for g in self.arg_gens]
        kwargs = {name: next(g) for name, g in self.kwarg_gens.items()}
        return self.callable(*args, **kwargs)

    def reset(self, seed):
        super().reset(seed)

    def _spawn(self, spawn_mapping):
        return Apply(self.callable, spawn_mapping=spawn_mapping, *self.arg_gens_orig, **self.kwarg_gens_orig)


class Lookup(Apply):

    def __init__(self, g, mapping):
        self.g = g
        self.mapping = mapping

        def f_lookup(key):
            return mapping[key]

        super().__init__(f_lookup, g)

    def _spawn(self, spawn_mapping):
        return Lookup(self.g, self.mapping)


class SelectOneDerived(Apply):

    def __init__(self, parent, p=None):
        self.parent = as_tohu_generator(parent)
        self.p = as_tohu_generator(p)
        self.randgen = Random()
        func = self.randgen.choice
        super().__init__(func, parent)

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(next(self.seed_generator))

    def _spawn(self, spawn_mapping):
        return SelectOneDerived(self.parent, self.p)

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())
