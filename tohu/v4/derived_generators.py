from functools import partial
from operator import attrgetter, getitem

from .base import TohuBaseGenerator, SeedGenerator

__all__ = ['Apply', 'GetAttribute', 'Lookup']


class FuncArgGens:
    """
    Helper class
    """

    def __init__(self, arg_gens, kwarg_gens):
        self.arg_gens = arg_gens
        self.kwarg_gens = kwarg_gens
        self.seed_generator = SeedGenerator()

    def __next__(self):
        next_args = [next(g) for g in self.arg_gens]
        next_kwargs = {name: next(g) for name, g in self.kwarg_gens.items()}
        return next_args, next_kwargs

    def spawn(self):
        arg_gens_spawned = [g.spawn() for g in self.arg_gens]
        kwarg_gens_spawned = {name: g.spawn() for name, g in self.kwarg_gens.items()}
        return FuncArgGens(arg_gens_spawned, kwarg_gens_spawned)

    def clone(self):
        arg_gens_spawned = [g.clone() for g in self.arg_gens]
        kwarg_gens_spawned = {name: g.clone() for name, g in self.kwarg_gens.items()}
        return FuncArgGens(arg_gens_spawned, kwarg_gens_spawned)

    @property
    def all_generators(self):
        """
        Convenience property to iterate over all generators in arg_gens and kwarg_gens.
        """
        for arg_gen in self.arg_gens:
            yield arg_gen

        for kwarg_gen in self.kwarg_gens.values():
            yield kwarg_gen

    def reset(self, seed):
        self.seed_generator.reset(seed)

        for g in self.all_generators:
            g.reset(next(self.seed_generator))


class Apply(TohuBaseGenerator):

    def __init__(self, func, *arg_gens, **kwarg_gens):
        super().__init__()
        self._check_func_is_callable(func)
        self.func = func
        self.func_arg_gens_orig = FuncArgGens(arg_gens, kwarg_gens)
        self.func_arg_gens_internal = self.func_arg_gens_orig.clone()

    def _check_func_is_callable(self, func):
        if not callable(func):
            raise TypeError("First argument must be callable. Got: {func} (type: {type(func)})")

    def __next__(self):
        next_args, next_kwargs = next(self.func_arg_gens_internal)
        return self.func(*next_args, **next_kwargs)

    def reset(self, seed):
        super().reset(seed)
        self.func_arg_gens_internal.reset(seed)

    def spawn(self):
        return Apply(self.func, *self.func_arg_gens_orig.arg_gens, **self.func_arg_gens_orig.kwarg_gens)


class GetAttribute(Apply):

    def __init__(self, parent, name):
        self.parent = parent  # no need to clone here because this happens in the superclass
        self.name = name
        func = attrgetter(self.name)
        super().__init__(func, self.parent)

    def spawn(self):
        return GetAttribute(self.parent, self.name)


class Lookup(Apply):

    def __init__(self, parent, mapping):
        self.parent = parent  #  no need to clone here because this happens in the superclass
        self.mapping = mapping
        func = partial(getitem, self.mapping)
        super().__init__(func, parent)

    def spawn(self):
        return Lookup(self.parent, self.mapping)
