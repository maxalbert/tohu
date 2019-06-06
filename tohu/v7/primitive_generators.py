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


class Incremental(PrimitiveGenerator):
    """
    Generator which produces integers that increase in regular steps.
    """

    def __init__(self, *, start=1, step=1):
        """
        Parameters
        ----------
        start : int, optional
            Start value of the sequence (default: 1).
        step : int, optional
            Step size of the sequence (default: 1).

        Example
        -------
        >>> g = Incremental(start=200, step=4)
        >>> list(g.generate(num=10))
        [200, 204, 208, 212, 216, 220, 224, 228, 232, 236]
        """
        super().__init__()
        self.start = start
        self.step = step
        self.cur_value = start

    def __next__(self):
        retval = self.cur_value
        self.cur_value += self.step
        return retval

    def reset(self, seed=None):
        super().reset(seed)
        self.cur_value = self.start
        return self

    # def _set_state_from(self, other):
    #     super()._set_state_from(other)
    #     self.start = other.start
    #     self.cur_value = other.cur_value
