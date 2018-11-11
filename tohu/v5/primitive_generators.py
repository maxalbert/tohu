import numpy as np
from faker import Faker
from functools import partial
from random import Random
from .base import TohuBaseGenerator
from .logging import logger
from .utils import identity

__all__ = ['Boolean', 'CharString', 'Constant', 'DigitString', 'FakerGenerator', 'Float', 'HashDigest', 'Integer', 'PrimitiveGenerator', 'SelectOne']


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
        self.randgen.seed(next(self.seed_generator))
        return self

    def __next__(self):
        return self.randgen.random() < self.p

    def spawn(self):
        new_obj = Boolean(self.p)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
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
        self.randgen.seed(next(self.seed_generator))
        return self

    def __next__(self):
        return self.randgen.randint(self.low, self.high)

    def spawn(self):
        new_obj = Integer(self.low, self.high)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())


class Float(PrimitiveGenerator):
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
        self.randgen.seed(next(self.seed_generator))
        return self

    def __next__(self):
        return self.randgen.uniform(self.low, self.high)

    def spawn(self):
        new_obj = Float(self.low, self.high)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())


CHARACTER_SETS = {
    '<alphanumeric>': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    '<alphanumeric_lowercase>': 'abcdefghijklmnopqrstuvwxyz0123456789',
    '<alphanumeric_uppercase>': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    '<lowercase>': 'abcdefghijklmnopqrstuvwxyz',
    '<uppercase>': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    '<digits>': '0123456789',
}


class CharString(PrimitiveGenerator):
    """
    Generator which produces a sequence of character strings.
    """

    def __init__(self, *, length, charset='<alphanumeric>'):
        """
        Parameters
        ----------
        length: integer
            Length of the character strings produced by this generator.
        charset: iterable
            Character set to draw from when generating strings, or string
            with the name of a pre-defined character set.
            Default: <alphanumeric> (both lowercase and uppercase letters).
        """
        super().__init__()
        self.length = length
        try:
            self.charset = CHARACTER_SETS[charset]
            logger.debug(f"Using pre-defined character set: '{charset}'")
        except KeyError:
            self.charset = charset
        self.char_gen = Random()

    def spawn(self):
        new_obj = CharString(length=self.length, charset=self.charset)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.char_gen.setstate(other.char_gen.getstate())

    def __next__(self):
        chars = self.char_gen.choices(self.charset, k=self.length)
        return ''.join(chars)

    def reset(self, seed):
        super().reset(seed)
        self.char_gen.seed(next(self.seed_generator))
        return self


class DigitString(CharString):
    """
    Generator which produces a sequence of strings containing only digits.
    """

    def __init__(self, *, length=None):
        """
        Parameters
        ----------
        length: integer
            Length of the character strings produced by this generator.
        """
        charset = "0123456789"
        super().__init__(length=length, charset=charset)

    def spawn(self):
        new_obj = DigitString(length=self.length)
        new_obj._set_random_state_from(self)
        return new_obj


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
        super()._set_random_state_from(other)
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
        super()._set_random_state_from(other)
        self.fake.random.setstate(other.fake.random.getstate())


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
        self.values = list(values)  # convert values to a list so that numpy.random.RandomState() doesn't get confused
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
        self.randgen.seed(next(self.seed_generator))
        return self

    def spawn(self):
        new_obj = SelectOne(self.values, p=self.p)
        new_obj._set_random_state_from(self)
        return new_obj
