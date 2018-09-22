from abc import ABCMeta, abstractmethod
import numpy as np
from faker import Faker
from random import Random
from .utils import identity
from ..item_list import ItemList

PRIMITIVE_GENERATORS = ['Constant', 'FakerGenerator', 'HashDigest', 'Integer', 'IterateOver', 'SelectOne']

__all__ = PRIMITIVE_GENERATORS + ['PRIMITIVE_GENERATORS']


class PrimitiveGenerator(metaclass=ABCMeta):
    """
    Base class for all primitive generators
    """
    def __init__(self):
        self._clones = []

    def register_clone(self, clone):
        self._clones.append(clone)

    @abstractmethod
    def __next__(self):
        raise NotImplementedError("Class {} does not implement method '__next__'.".format(self.__class__.__name__))

    @abstractmethod
    def reset(self, seed):
        for c in self._clones:
            c.reset(seed)


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
        super().reset(seed)
        return self

    def __next__(self):
        return self.value


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
        self.low = low
        self.high = high
        self.randgen = Random()
        self._clones = []

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)
        return self

    def __next__(self):
        return self.randgen.randint(self.low, self.high)

    def register_clone(self, clone):
        self._clones.append(clone)


class HashDigest(PrimitiveGenerator):
    """
    Generator which produces a sequence of hex strings representing hash digest values.
    """

    def __init__(self, *, length=None, as_bytes=False, uppercase=True):
        """
        Parameters
        ----------
        length: integer
            Length of the character strings produced by this generator.
        as_bytes: bool
            If True, return `length` random bytes. If False, return a string of `length`
            characters with a hexadecimal representation of `length/2` random bytes.
            Note that in the second case `length` must be an even number.
        uppercase: bool
            If True (the default), return hex string using uppercase letters, otherwise lowercase.
            This only has an effect if `as_bytes=False`.
        """
        super().__init__()
        self.length = length
        self._internal_length = length if as_bytes else length / 2
        if not as_bytes and (length % 2) != 0:
            raise ValueError(
                f"Length must be an even number if as_bytes=False because it "
                f"represents length = 2 * num_random_bytes. Got: length={length})")
        self.as_bytes = as_bytes
        self.uppercase = uppercase
        self.randgen = np.random.RandomState()
        self._maybe_convert_to_hex = identity if self.as_bytes else bytes.hex
        self._maybe_convert_to_uppercase = identity if (self.as_bytes or not uppercase) else str.upper

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)
        return self

    def __next__(self):
        val = self.randgen.bytes(self._internal_length)
        return self._maybe_convert_to_uppercase(self._maybe_convert_to_hex(val))


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

    def reset(self, seed):
        super().reset(seed)
        self.fake.seed_instance(seed)
        return self

    def __next__(self):
        return self.randgen(**self.faker_args)


class IterateOver(PrimitiveGenerator):
    """
    Generator which simply iterates over all items in a given iterable
    """

    def __init__(self, seq):
        assert isinstance(seq, (list, tuple, ItemList, str)), \
            "For the time being we enforce g being a list, tuple, ItemList or string so that we can spawn and reset this generator."
        super().__init__()
        self.seq = seq
        self.gen = None
        self.reset()

    def __repr__(self):
        return f"<IterateOver, list with {len(self.seq)} items>"

    def __next__(self):
        return next(self.gen)

    def __iter__(self):
        return self

    def reset(self, seed=None):
        super().reset(seed)
        self.gen = iter(self.seq)
        return self


class SelectOne(PrimitiveGenerator):
    """
    Generator which produces a sequence of items taken from a given set of elements.
    """

    def __init__(self, values, p=None):
        """
        Parameters
        ----------
        values: list
            List of options from which to choose elements.
        p: list, optional
            The probabilities associated with each element in `values`.
            If not given the assumes a uniform distribution over all values.
        """
        super().__init__()
        self.values = values
        self.p = p
        self.randgen = np.random.RandomState()
        self.num_values = len(values)

    def __next__(self):
        idx = self.randgen.choice(self.num_values, p=self.p)
        return self.values[idx]

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)
        return self
