from .base import TohuBaseGenerator

__all__ = ['Apply']


class DerivedGenerator(TohuBaseGenerator):
    """
    Base class for all derived generators
    """


class Apply(DerivedGenerator):

    def __init__(self, callable, *arg_gens, **kwarg_gens):
        super().__init__()
        self.callable = callable
        self.arg_gens_orig = arg_gens
        self.kwarg_gens_orig = kwarg_gens

        self.arg_gens = [g.clone() for g in self.arg_gens_orig]
        self.kwarg_gens = {name: g.clone() for name, g in self.kwarg_gens_orig.items()}
        self._input_generators = [g for g in self.arg_gens_orig] + [g for g in self.kwarg_gens_orig.values()]
        self._constituent_generators = [g for g in self.arg_gens] + [g for g in self.kwarg_gens.values()]

    def __next__(self):
        args = [next(g) for g in self.arg_gens]
        kwargs = {name: next(g) for name, g in self.kwarg_gens.items()}
        return self.callable(*args, **kwargs)

    def reset(self, seed):
        super().reset(seed)

    def spawn(self):
        return Apply(self.callable, *self.arg_gens_orig, **self.kwarg_gens_orig)
