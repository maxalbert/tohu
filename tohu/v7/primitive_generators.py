from random import Random
from .base import PrimitiveGenerator


class Constant(PrimitiveGenerator):
    """
    Generator which produces a constant sequence (repeating the same value indefinitely).
    """

    def __init__(self, value):
        """
        Parameters
        ----------
        value:
            The constant value produced by this generator.
        """
        super().__init__()
        self.value = value

    def reset(self, seed=None):
        """
        Note that this method supports the `seed` argument (for consistency with other generators),
        but its value is ignored because resetting a Constant generator has no effect.
        """
        super().reset(seed)
        return self

    def __next__(self):
        return self.value

    # def _set_state_from(self, other):
    #     pass


class Boolean(PrimitiveGenerator):
    """
    Generator which produces random boolean values (True or False) with a given probability.
    """

    def __init__(self, p=0.5):
        """
        Parameters
        ----------
        p: float
            The probability that True is returned. Must be between 0.0 and 1.0.
        """
        super().__init__()
        self.p = p
        self.randgen = Random()

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)
        return self

    def __next__(self):
        return self.randgen.random() < self.p

    # def _set_state_from(self, other):
    #     self.randgen.setstate(other.randgen.getstate())
