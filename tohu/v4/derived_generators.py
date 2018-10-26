import inspect
import re

from functools import partial
from operator import attrgetter, getitem
from random import Random

from .base import TohuBaseGenerator, SeedGenerator
from .primitive_generators import as_tohu_generator

__all__ = ['Apply', 'GetAttribute', 'Lookup', 'SelectOneDerived', 'SelectMultipleDerived', 'TohuDict', 'fstr', 'ifthen']


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

    def _set_random_state_from(self, other):
        # Sanity checks
        assert isinstance(other, FuncArgGens)
        assert len(self.arg_gens) == len(other.arg_gens)
        assert len(self.kwarg_gens) == len(other.kwarg_gens)

        self.seed_generator._set_random_state_from(other.seed_generator)

        # Transfer random state from individual arg_gens
        for arg_gen_self, arg_gen_other in zip(self.arg_gens, other.arg_gens):
            arg_gen_self._set_random_state_from(arg_gen_other)

        # Transfer random state from individual kwarg_gens
        for name in self.kwarg_gens.keys():
            kwarg_gen_self = self.kwarg_gens[name]
            kwarg_gen_other = other.kwarg_gens[name]
            kwarg_gen_self._set_random_state_from(kwarg_gen_other)


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

    def spawn(self):
        new_obj = Apply(self.func, *self.func_arg_gens_orig.arg_gens, **self.func_arg_gens_orig.kwarg_gens)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        #self.func_arg_gens_orig._set_random_state_from(other.func_arg_gens_orig)
        self.func_arg_gens_internal._set_random_state_from(other.func_arg_gens_internal)


class GetAttribute(Apply):

    def __init__(self, parent, name):
        self.parent = parent  # no need to clone here because this happens in the superclass
        self.name = name
        func = attrgetter(self.name)
        super().__init__(func, self.parent)

    def spawn(self):
        return GetAttribute(self.parent, self.name)

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)


class Lookup(Apply):

    def __init__(self, parent, mapping):
        self.parent = parent  #  no need to clone here because this happens in the superclass
        self.mapping = mapping
        func = partial(getitem, self.mapping)
        super().__init__(func, parent)

    def spawn(self):
        return Lookup(self.parent, self.mapping)

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)


class SelectOneDerived(Apply):

    def __init__(self, parent, p=None):
        self.parent = as_tohu_generator(parent)
        self.p = as_tohu_generator(p)
        self.randgen = Random()
        func = self.randgen.choice
        super().__init__(func, parent)

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)

    def spawn(self):
        return SelectOneDerived(self.parent, self.p)

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())


# TODO: find a better name for this class!
class SelectMultipleDerived(Apply):

    def __init__(self, parent, num):
        assert isinstance(parent, TohuBaseGenerator)
        assert isinstance(num, TohuBaseGenerator)
        self.parent = parent
        self.num = num
        self.randgen = Random()
        func = self.randgen.choices
        super().__init__(func, parent, k=self.num)

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)

    def spawn(self):
        return SelectMultipleDerived(self.parent, self.num)

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())


class fstr(Apply):
    """
    Helper function for easy formatting of generators.

    Usage example:

        >>> g1 = Integer(100, 200)
        >>> g2 = Integer(300, 400)
        >>> g3 = g1 + g2
        >>> h = fstr('{g1} + {g2} = {g3}')
        >>> print(next(h))
        122 + 338 = 460
        >>> print(next(h))
        165 + 325 = 490
    """

    def __init__(self, spec, namespace=None):

        # FIXME: this pattern is not yet compatible with the full f-string spec.
        # For example, it doesn't recognise double '{{' and '}}' (for escaping).
        # Also it would be awesome if we could parse arbitrary expressions inside
        # the curly braces.
        pattern = '{([^}]+)}'

        gen_names = re.findall(pattern, spec)

        if namespace is None:
            namespace = inspect.currentframe().f_back.f_globals
            namespace.update(inspect.currentframe().f_back.f_locals)

        gens = {name: namespace[name] for name in gen_names}

        def format_items(**kwargs):
            return spec.format(**kwargs)

        super().__init__(format_items, **gens)

    def spawn(self):
        raise NotImplemented("TODO: check which namespace to use when spawning an instance of 'fstr'")


class TohuDict:
    """
    Helper class which behaves like a regular dictionary but
    also allows easy lookup of items produced by a generator.
    """

    def __init__(self, mapping):
        self.mapping = mapping

    def __getitem__(self, key):
        if isinstance(key, TohuBaseGenerator):
            return Lookup(key, self.mapping)
        else:
            return self.mapping[key]


class ifthen(Apply):

    def __init__(self, g_cond, g_true, g_false):
        """
        Parameters
        ----------
        g_cond: tohu.generator

        :param g_cond:
        :param g_true:
        :param g_false:
        """
        self.g_cond = g_cond
        self.g_true = g_true
        self.g_false = g_false

        def func(cond, x, y):
            return x if cond else y

        super().__init__(func, self.g_cond, as_tohu_generator(self.g_true), as_tohu_generator(self.g_false))

    def spawn(self):
        return ifthen(self.g_cond, self.g_true, self.g_false)
