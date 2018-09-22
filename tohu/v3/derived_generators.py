from .base import TohuBaseGenerator

DERIVED_GENERATORS = ['Apply']

__all__ = DERIVED_GENERATORS + ['DERIVED_GENERATORS']


class Apply(TohuBaseGenerator):

    def __init__(self, func, *arg_gens, **kwarg_gens):
        super().__init__()
        self.func = func
        self.orig_arg_gens = arg_gens
        self.orig_kwarg_gens = kwarg_gens

        self.arg_gens = [g.clone() for g in arg_gens]
        self.kwarg_gens = {name: g.clone() for name, g in kwarg_gens.items()}

    def __next__(self):
        next_args = (next(g) for g in self.arg_gens)
        next_kwargs = {name: next(g) for name, g in self.kwarg_gens.items()}
        return self.func(*next_args, **next_kwargs)

    def reset(self, seed=None):
        super().reset(seed)

    def spawn(self):
        return Apply(self.func, *self.orig_arg_gens, **self.orig_kwarg_gens)