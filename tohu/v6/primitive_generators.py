import datetime as dt
import numpy as np

from faker import Faker
from random import Random

from .base import TohuBaseGenerator
from .utils import ensure_is_date_object, identity, ensure_is_datetime_object

__all__ = ['Constant', 'FakerGenerator', 'Date', 'HashDigest', 'Integer', 'Timestamp']


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

    def spawn(self, spawn_mapping=None):
        return Constant(self.value)

    def _set_random_state_from(self, other):
        pass


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

    def spawn(self, spawn_mapping=None):
        new_obj = Integer(self.low, self.high)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
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

    def spawn(self, spawn_mapping=None):
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

    def spawn(self, spawn_mapping=None):
        new_obj = FakerGenerator(self.method, locale=self.locale, **self.faker_args)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.fake.random.setstate(other.fake.random.getstate())


def as_tohu_generator(g):
    """
    Helper function to ensure that a given input is a tohu generator.

    If g is already a tohu generator then it is returned unchanged,
    otherwise it is wrapped in a Constant generator.
    """

    if isinstance(g, TohuBaseGenerator):
        return g
    else:
        return Constant(g)


class TimestampError(Exception):
    """
    Custom exception for tohu Timestamps.
    """


class Timestamp(TohuBaseGenerator):

    def __init__(self, start, end):
        super().__init__()
        self.start = ensure_is_datetime_object(start)
        self.end = ensure_is_datetime_object(end, optional_offset=dt.timedelta(hours=23, minutes=59, seconds=59))
        self.interval = (self.end - self.start).total_seconds()
        self.offset_randgen = Random()
        self._check_start_before_end()

    def _check_start_before_end(self):
        if self.start > self.end:
            raise TimestampError(f"Start value must be before end value. Got: start={self.start}, end={self.end}")

    def __next__(self):
        offset = self.offset_randgen.randint(0, self.interval)
        return self.start + dt.timedelta(seconds=offset)

    def reset(self, seed):
        super().reset(seed)
        self.offset_randgen.seed(next(self.seed_generator))

    def spawn(self, spawn_mapping=None):
        new_obj = Timestamp(self.start, self.end)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.offset_randgen.setstate(other.offset_randgen.getstate())


class Date(TohuBaseGenerator):

    def __init__(self, start, end):
        super().__init__()
        self.start = ensure_is_date_object(start)
        self.end = ensure_is_date_object(end)
        self.interval = (self.end - self.start).days
        self.offset_randgen = Random()
        self._check_start_before_end()

    def _check_start_before_end(self):
        if self.start > self.end:
            raise TimestampError(f"Start value must be before end value. Got: start={self.start}, end={self.end}")

    def __next__(self):
        offset = self.offset_randgen.randint(0, self.interval)
        return self.start + dt.timedelta(days=offset)

    def reset(self, seed):
        super().reset(seed)
        self.offset_randgen.seed(next(self.seed_generator))

    def spawn(self, spawn_mapping=None):
        new_obj = Date(self.start, self.end)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.offset_randgen.setstate(other.offset_randgen.getstate())
