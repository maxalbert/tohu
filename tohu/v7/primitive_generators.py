import numpy as np
from faker import Faker
from random import Random
from .base import PrimitiveGenerator
from .utils import identity

__all__ = ["Constant", "Boolean", "FakerGenerator", "HashDigest", "Incremental", "Integer"]


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


class Integer(PrimitiveGenerator):
    """
    Generator which produces random integers k in the range low <= k <= high.
    """

    def __init__(self, low, high):
        """
        Parameters
        ----------
        low: integer
            Lower bound (inclusive).
        high: integer
            Upper bound (inclusive).
        """
        super().__init__()
        self.low = low
        self.high = high
        self.randgen = Random()

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(next(self.seed_generator))
        return self

    def __next__(self):
        return self.randgen.randint(self.low, self.high)

    # def _set_state_from(self, other):
    #     super()._set_state_from(other)
    #     self.randgen.setstate(other.randgen.getstate())


class HashDigest(PrimitiveGenerator):
    """
    Generator which produces a sequence of hex strings representing hash digest values.
    """

    def __init__(self, *, length, as_bytes=False, lowercase=False):
        """
        Parameters
        ----------
        length: integer
            Length of the character strings produced by this generator.
        as_bytes: bool, optional
            If True, return `length` random bytes. If False, return a string
            containing `length` characters (which represents the hex values of
            a sequence of  `length/2` random bytes). Note that in the second
            case `length` must be an even number.
        lowercase: bool, optional
            If True, return the hex string using lowercase letters. The default
            uses uppercase letters. This only has an effect if `as_bytes=False`.
        """
        super().__init__()
        self.length = length
        self._internal_length = length if as_bytes else length / 2
        if not as_bytes and (length % 2) != 0:
            raise ValueError(
                f"Length must be an even number if as_bytes=False because it "
                f"represents length = 2 * num_random_bytes. Got: length={length})")
        self.as_bytes = as_bytes
        self.lowercase = lowercase
        self.randgen = np.random.RandomState()
        self._maybe_convert_to_hex = identity if self.as_bytes else bytes.hex
        self._maybe_convert_to_uppercase = identity if (self.as_bytes or lowercase) else str.upper

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)
        return self

    def __next__(self):
        val = self.randgen.bytes(self._internal_length)
        return self._maybe_convert_to_uppercase(self._maybe_convert_to_hex(val))

    # def _set_random_state_from(self, other):
    #     super()._set_state_from(other)
    #     self.randgen.set_state(other.randgen.get_state())


class FakerGenerator(PrimitiveGenerator):
    """
    Generator which produces random elements using one of the methods supported by faker. [1]

    [1] https://faker.readthedocs.io/
    """

    def __init__(self, method, *, locale=None, **faker_args):
        """
        Parameters
        ----------
        method: string
            Name of the faker provider to use (see [1] for details)
        locale: string
             Locale to use when generating data, e.g. 'en_US' (see [1] for details)
        faker_args:
            Remaining arguments passed to the faker provider (see [1] for details)

        References
        ----------
        [1] https://faker.readthedocs.io/
        """
        super().__init__()
        self.method = method
        self.locale = locale
        self.faker_args = faker_args

        self.fake = Faker(locale=locale)
        self.randgen = getattr(self.fake, method)
        self.fake.seed_instance(None)  # seed instance to ensure we are decoupled from the global random state

    def reset(self, seed):
        super().reset(seed)
        self.fake.seed_instance(seed)
        return self

    def __next__(self):
        return self.randgen(**self.faker_args)

    # def _set_state_from(self, other):
    #     super()._set_state_from(other)
    #     self.fake.random.setstate(other.fake.random.getstate())
