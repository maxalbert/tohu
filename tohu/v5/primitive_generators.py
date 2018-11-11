from random import Random
from .base import TohuBaseGenerator
from .logging import logger

__all__ = ['Boolean', 'CharString', 'Constant', 'DigitString', 'Float', 'Integer', 'PrimitiveGenerator']


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
