from .base import DerivedGenerator, SeedGenerator


class Apply(DerivedGenerator):
    def __init__(self, func, *input_args, **input_kwargs):
        super().__init__()
        self.func = func
        self.input_args = input_args
        self.input_kwargs = input_kwargs
        self.arg_gens = [g.clone() for g in self.input_args]
        self.kwarg_gens = {name: g.clone() for name, g in self.input_kwargs.items()}

    def __next__(self):
        args = [next(g) for g in self.arg_gens]
        kwargs = {name: next(g) for name, g in self.kwarg_gens.items()}
        return self.func(*args, **kwargs)

    def reset(self, seed):
        super().reset(seed)

    def _reset_argument_generators(self, seed):
        """
        Note: this method only exists for testing. Under normal
        circumstances the argument generators to a derived generator
        will be reset externally.
        """
        seed_gen = SeedGenerator().reset(seed)
        for g in self.arg_gens:
            g.reset(next(seed_gen))
        for h in self.kwarg_gens.values():
            h.reset(next(seed_gen))

    def spawn(self):
        new_obj = Apply(self.func, *self.input_args, **self.input_kwargs)
        new_obj._set_state_from(self)
        return new_obj

    def _set_state_from(self, other):
        super()._set_state_from(other)
        for g1, g2 in zip(self.arg_gens, other.arg_gens):
            g1._set_state_from(g2)
