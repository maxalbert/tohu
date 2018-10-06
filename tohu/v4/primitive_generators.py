import numpy as np

from faker import Faker
from functools import partial
from random import Random

from .base import TohuBaseGenerator
from .item_list import ItemList
from .utils import identity

__all__ = ['Boolean', 'Constant', 'FakerGenerator', 'Float', 'HashDigest', 'Integer', 'IterateOver', 'SelectOne', 'as_tohu_generator']


class PrimitiveGenerator(TohuBaseGenerator):
    """
    Base class for all primitive generators
    """


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

    def spawn(self):
        return Constant(self.value)

    def _set_random_state_from(self, other):
        pass


class Boolean(PrimitiveGenerator):
    """
    Generator which produces random boolean values (True or False).
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

    def spawn(self):
        new_obj = Boolean(self.p)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.randgen.setstate(other.randgen.getstate())


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
        self.randgen.seed(seed)
        return self

    def __next__(self):
        return self.randgen.randint(self.low, self.high)

    def spawn(self):
        new_obj = Integer(self.low, self.high)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.randgen.setstate(other.randgen.getstate())


class Float(TohuBaseGenerator):
    """
    Generator which produces random floating point numbers x in the range low <= x <= high.
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
        self.randgen.seed(seed)
        return self

    def __next__(self):
        return self.randgen.uniform(self.low, self.high)

    def spawn(self):
        new_obj = Float(self.low, self.high)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.randgen.setstate(other.randgen.getstate())


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

    def spawn(self):
        new_obj = HashDigest(length=self.length, as_bytes=self.as_bytes, uppercase=self.uppercase)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.randgen.set_state(other.randgen.get_state())


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

    def spawn(self):
        new_obj = FakerGenerator(self.method, locale=self.locale, **self.faker_args)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.fake.random.setstate(other.fake.random.getstate())



class IterateOver(PrimitiveGenerator):
    """
    Generator which simply iterates over all items in a given iterable
    """

    def __init__(self, seq):
        if not isinstance(seq, (list, tuple, ItemList, str)):
            raise TypeError(
                f"For the time being 'seq' must be a list, tuple, ItemList or string "
                f"so that we can reproducibly spawn and reset this generator. Got: {seq}")

        super().__init__()
        self.seq = seq
        # Note: iterating using an explicit index isn't ideal but it allows
        # to transfer the internal state when spawning (for reproducibility)
        self.idx = 0
        self.reset()

    def __repr__(self):
        return f"<IterateOver, list with {len(self.seq)} items>"

    def __next__(self):
        try:
            val = self.seq[self.idx]
        except IndexError:
            raise StopIteration()
        self.idx += 1
        return val

    def __iter__(self):
        return self

    def reset(self, seed=None):
        super().reset(seed)
        self.idx = 0
        return self

    def spawn(self):
        new_obj = IterateOver(self.seq)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.idx = other.idx


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
        self.values = list(values)  # need to convert to a list so that numpy.random.RandomState() doesn't get confused
        self.p = p
        self.randgen = None
        self.func_random_choice = None
        self._init_randgen()

    def _init_randgen(self):
        """
        Initialise random generator to be used for picking elements.
        With the current implementation in tohu (where we pick elements
        from generators individually instead of in bulk), it is faster
        to `use random.Random` than `numpy.random.RandomState` (it is
        possible that this may change in the future if we change the
        design so that tohu pre-produces elements in bulk, but that's
        not likely to happen in the near future).

        Since `random.Random` doesn't support arbitrary distributions,
        we can only use it if `p=None`. This helper function returns
        the appropriate random number generator depending in the value
        of `p`, and also returns a function `random_choice` which can be
        applied to the input sequence to select random elements from it.
        """
        if self.p is None:
            self.randgen = Random()
            self.func_random_choice = self.randgen.choice
        else:
            self.randgen = np.random.RandomState()
            self.func_random_choice = partial(self.randgen.choice, p=self.p)

    def _set_random_state_from(self, other):
        """
        Transfer the internal state from `other` to `self`.
        After this call, `self` will produce the same elements
        in the same order as `other` (even though they otherwise
        remain completely independent).
        """
        try:
            # this works if randgen is an instance of random.Random()
            self.randgen.setstate(other.randgen.getstate())
        except AttributeError:
            # this works if randgen is an instance of numpy.random.RandomState()
            self.randgen.set_state(other.randgen.get_state())

        return self

    def __next__(self):
        return self.func_random_choice(self.values)

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)
        return self

    def spawn(self):
        new_obj = SelectOne(self.values, p=self.p)
        new_obj._set_random_state_from(self)
        return new_obj


def as_tohu_generator(g):
    """
    Helper function which guarantees its return value
    to be a tohu generator.

    If the input `g` is already a tohu generator, it
    is returned unchanged. Otherwise it is wrapped
    in a Constant generator which returns the input
    value at each iteration.
    """

    if isinstance(g, TohuBaseGenerator):
        return g
    else:
        return Constant(g)
