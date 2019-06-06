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
