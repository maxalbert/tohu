__all__ = ['Constant']


class Constant:
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
        self.value = value

    def reset(self, seed=None):
        return self

    def __next__(self):
        return self.value
