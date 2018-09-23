import logging
from functools import partial
from operator import attrgetter, getitem
from random import Random
from .base import TohuBaseGenerator
from .dependency_graph import DependencyGraph

DERIVED_GENERATORS = ['Apply', 'GetAttribute', 'Lookup', 'SelectOneFromGenerator']

__all__ = DERIVED_GENERATORS + ['DERIVED_GENERATORS']

logger = logging.getLogger('tohu')


class Apply(TohuBaseGenerator):

    def __init__(self, func, *arg_gens, **kwarg_gens):
        super().__init__()
        self.func = func
        self.orig_arg_gens = list(arg_gens)
        self.orig_kwarg_gens = kwarg_gens

        self.arg_gens = [g.clone(gen_mapping=dict()) for g in self.orig_arg_gens]
        self.kwarg_gens = {name: g.clone(gen_mapping=dict()) for name, g in self.orig_kwarg_gens.items()}

    def __next__(self):
        next_args = (next(g) for g in self.arg_gens)
        next_kwargs = {name: next(g) for name, g in self.kwarg_gens.items()}
        return self.func(*next_args, **next_kwargs)

    def reset(self, seed=None):
        super().reset(seed)

    def spawn(self, gen_mapping=None):
        gen_mapping = gen_mapping or dict()
        g_new = Apply(self.func, *self.orig_arg_gens_rewired(gen_mapping), **self.orig_kwarg_gens_rewired(gen_mapping))
        gen_mapping[self] = g_new
        return g_new

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

    def add_to_dependency_graph(self, graph):
        sg_attr = dict(style='filled', fillcolor='/blues3/1', pencolor='gray')
        sg = DependencyGraph(name=f'cluster_{self.tohu_id}', graph_attr=sg_attr)

        sg.add_node(self)
        for c in self.arg_gens:
            c.add_to_dependency_graph(sg)
        for c in self.kwarg_gens.values():
            c.add_to_dependency_graph(sg)
        graph.add_subgraph(sg)

        for g in self.orig_arg_gens:
            g.add_to_dependency_graph(graph)
        for g in self.orig_kwarg_gens.values():
            g.add_to_dependency_graph(graph)


class GetAttribute(Apply):

    def __init__(self, parent, name):
        self.parent = parent  # no need to clone here because this happens in the superclass
        self.name = name
        func = attrgetter(name)
        super().__init__(func, parent)

    def spawn(self, gen_mapping):
        new_parent = gen_mapping.get(self.parent, self.parent)
        g_new = GetAttribute(new_parent, self.name)
        logger.debug(f'[DDD] Adding mapping: {self}  -->  {g_new}')
        gen_mapping[self] = g_new
        return g_new


class Lookup(Apply):

    def __init__(self, parent, mapping):
        self.parent = parent  #  no need to clone here because this happens in the superclass
        self.mapping = mapping
        func = partial(getitem, self.mapping)
        super().__init__(func, parent)

    def spawn(self, gen_mapping):
        new_parent = gen_mapping.get(self.parent, self.parent)
        logger.debug(f'[EEE] Lookup.spawn(): gen_mapping={gen_mapping}')
        logger.debug(f'[EEE] Lookup.spawn(): new_parent={new_parent}')
        g_new = Lookup(new_parent, self.mapping)
        logger.debug(f'[DDD] Adding mapping: {self}  -->  {g_new}')
        gen_mapping[self] = g_new
        return g_new


# TODO: find a better name for this class!
class SelectOneFromGenerator(Apply):

    def __init__(self, parent):
        self.parent = parent
        self.randgen = Random()
        func = self.randgen.choice
        super().__init__(func, parent)

    def reset(self, seed):
        self.randgen.seed(seed)

    def spawn(self, gen_mapping):
        new_parent = gen_mapping.get(self.parent, self.parent)
        g_new = SelectOneFromGenerator(new_parent)
        logger.debug(f'[DDD] Adding mapping: {self}  -->  {g_new}')
        gen_mapping[self] = g_new
        return g_new