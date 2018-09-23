from functools import partial
from operator import attrgetter, getitem
from random import Random
from .base import TohuBaseGenerator

DERIVED_GENERATORS = ['Apply', 'GetAttribute', 'Lookup', 'SelectOneFromGenerator']

__all__ = DERIVED_GENERATORS + ['DERIVED_GENERATORS']


class Apply(TohuBaseGenerator):

    def __init__(self, func, *arg_gens, **kwarg_gens):
        super().__init__()
        self.func = func
        self.orig_arg_gens = list(arg_gens)
        self.orig_kwarg_gens = kwarg_gens

        self.arg_gens = [g.clone() for g in arg_gens]
        self.kwarg_gens = {name: g.clone() for name, g in kwarg_gens.items()}

    def __next__(self):
        next_args = (next(g) for g in self.arg_gens)
        next_kwargs = {name: next(g) for name, g in self.kwarg_gens.items()}
        return self.func(*next_args, **next_kwargs)

    def reset(self, seed=None):
        super().reset(seed)

    def spawn(self, gen_mapping=None):
        gen_mapping = gen_mapping or dict()
        return Apply(self.func, *self.orig_arg_gens_rewired(gen_mapping), **self.orig_kwarg_gens_rewired(gen_mapping))

    @property
    def input_generators(self):
        """
        Return list of all (original) input generators which feed into this derived generator.
        """
        return self.orig_arg_gens + list(self.orig_kwarg_gens.values())

    def orig_arg_gens_rewired(self, gen_mapping):
        return [gen_mapping.get(g, g) for g in self.orig_arg_gens]

    def orig_kwarg_gens_rewired(self, gen_mapping):
        return {name: gen_mapping.get(g, g) for name, g in self.orig_kwarg_gens.items()}

    def rewire(self, gen_mapping):
        """

        """
        for i, g in enumerate(self.orig_arg_gens):
            try:
                g_new = gen_mapping[g]
                self.orig_arg_gens[i] = g_new
                self.arg_gens[i] = g_new.clone()
            except KeyError:
                pass

        for name, g in self.orig_kwarg_gens.items():
            try:
                g_new = gen_mapping[g]
                self.orig_kwarg_gens[name] = g_new
                self.kwarg_gens[name] = g_new.clone()
            except KeyError:
                pass


class GetAttribute(Apply):

    def __init__(self, parent, name):
        self.parent = parent  # no need to clone here because this happens in the superclass
        self.name = name
        func = attrgetter(name)
        super().__init__(func, parent)

    def spawn(self, gen_mapping=None):
        gen_mapping = gen_mapping or dict()
        new_parent = gen_mapping.get(self.parent, self.parent)
        return GetAttribute(new_parent, self.name)


class Lookup(Apply):

    def __init__(self, parent, mapping):
        self.parent = parent  #  no need to clone here because this happens in the superclass
        self.mapping = mapping
        func = partial(getitem, self.mapping)
        super().__init__(func, parent)

    def spawn(self, gen_mapping):
        gen_mapping = gen_mapping or dict()
        new_parent = gen_mapping.get(self.parent, self.parent)
        return Lookup(new_parent, self.mapping)


# TODO: find a better name for this class!
class SelectOneFromGenerator(Apply):

    def __init__(self, parent):
        self.parent = parent
        self.randgen = Random()
        func = self.randgen.choice
        super().__init__(func, parent)

    def reset(self, seed):
        self.randgen.seed(seed)

    def spawn(self, gen_mapping=None):
        gen_mapping = gen_mapping or dict()
        new_parent = gen_mapping.get(self.parent, self.parent)
        return SelectOneFromGenerator(new_parent)