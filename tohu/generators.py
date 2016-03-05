# -*- coding: utf-8 -*-
"""
Generator classes to produce random elements with specific properties.

Note that all non-trivial generators in this module allow passing
custom random number generators, which is useful for testing purposes.
If a custom random number generator is provided then it is the
caller's responsibility to ensure that it generates random elements
with the correct constraints (for example, integers in the expected
range).

"""

import datetime as dt
import dateutil.parser
from itertools import count
from random import Random

from .random_generators import new_seed, RandFloat, RandInt


class Constant:
    """
    Generator which always returns the same fixed value.
    """

    def __init__(self, value):
        self.value = value

    def seed(self, seed):
        """
        Setting the seed on a 'Constant' object has no effect.
        This method only exists to provide a consistent interface.
        """

    def next(self):
        """
        Return the fixed value provided during initialisation.
        """
        return self.value


class Empty:
    """
    Generator which always returns the empty string.
    """

    def next(self):
        """
        Return the empty string.
        """
        return ""

    def seed(self, seed):
        """
        Setting the seed on an 'Empty' object has no effect.
        This method only exists to provide a consistent interface.
        """


class Sequential:
    """
    Generator which returns a sequence of strings of the form '<prefix>XXXX',
    where <prefix> is a customisable string and XXXX represents a sequentially
    increasing counter.

    Example:

    >>> seq = Sequential(prefix='Foobar', digits=3)
    >>> seq.next()
    Foobar001
    >>> seq.next()
    Foobar002
    >>> seq.next()
    Foobar003

    """

    def __init__(self, prefix, digits=4):
        """
        Initialise generator with the given prefix.
        """
        self.prefix = prefix
        self.cnt = count(start=1)
        self.fmt_str = self.prefix + '{{:0{digits}}}'.format(digits=digits)

    def seed(self, seed):
        """
        Setting the seed on a 'Sequential' object has no effect.
        This method only exists to provide a consistent interface.
        """

    def next(self):
        """
        Return next element in the sequence.
        """
        return self.fmt_str.format(next(self.cnt))

    def __call__(self, *args, **kwargs):
        """
        Return the object itself. This is useful so that we can use
        objects of type `Sequential` to mock other types of generators
        in our tests.
        """
        return self


class RandRange:
    """
    Random number generator which when called returns
    a random integer k satisfying minval <= k <= maxval.

    """

    def __init__(self, *args, seed=None):
        """
        Initialise random number generator.

        RandRange(maxval)         -> RandRange object
        RandRange(minval, maxval) -> RandRange object

        Args:
            minval (int): Lower bound (inclusive) for the sampled values.
            maxval (int): Upper bound (exclusive) for the sampled values.

        """
        if len(args) == 1:
            minval, maxval = 0, args[0]
        elif len(args) == 2:
            minval, maxval = args
        else:
            raise ValueError("RandRange can only accept <= 2 arguments.")

        self.randgen = Random()
        self.seed(seed or new_seed())
        self.minval = minval
        self.maxval = maxval

    # [DUPLICATE] seed #1
    def seed(self, seed):
        """
        Initialize random number generator with given seed.
        """
        self.randgen.seed(seed)

    def next(self):
        """
        Return random integer between `minval` (inclusive) and `maxval` (exclusive).
        """
        return self.randgen.randrange(self.minval, self.maxval)


class RandIntString:
    """
    Random generator which when returns strings representing random
    integers between 0 and maxval (both inclusive).

    """

    def __init__(self, *args, seed=None):
        """
        Initialise random number generator.

        RandIntString(maxval)         -> RandIntString object
        RandIntString(minval, maxval) -> RandIntString object

        Args:
            minval (int): Lower bound (inclusive) for the sampled values.
            maxval (int): Upper bound (exclusive) for the sampled values.

        """
        if len(args) == 1:
            self.minval = 0
            self.maxval = args[0]
        elif len(args) == 2:
            self.minval = args[0]
            self.maxval = args[1]
        else:
            raise ValueError("RandIntString can only accept <= 2 arguments.")

        self.randgen = Random()
        self.seed(seed or new_seed())

    # [DUPLICATE] seed #2
    def seed(self, seed):
        """
        Initialize random number generator with given seed.
        """
        self.randgen.seed(seed)

    def next(self):
        """
        Return string representing random integer between `minval` and `maxval` (both inclusive).
        """
        return str(self.randgen.randint(self.minval, self.maxval))


class Latitude:
    """
    Random number generator which when called returns random floats
    between -90 and +90 representing a latitude.

    """

    def __init__(self, *, randgen=None):
        """
        Initialise latitude generator.

        Args:

            randgen: Custom random number generator (useful for testing).
        """
        self.randgen = randgen or RandFloat(-90., 90.)

    def next(self):
        """
        Return random latitude.
        """
        return str(self.randgen.next())

    # [DUPLICATE] seed #3
    def seed(self, seed):
        """
        Initialize random number generator with given seed.
        """
        self.randgen.seed(seed)


class Longitude:
    """
    Random number generator which when called returns random floats
    between -180 and +180 representing a longitude.

    """

    def __init__(self, *, randgen=None):
        """
        Initialise longitude generator.

        Args:

            randgen: Custom random number generator (useful for testing).
        """
        self.randgen = randgen or RandFloat(-180., 180.)

    def next(self):
        """
        Return random longitude.
        """
        return str(self.randgen.next())

    # [DUPLICATE] seed #5
    def seed(self, seed):
        """
        Initialize random number generator with given seed.
        """
        self.randgen.seed(seed)


class TimestampError(Exception):
    """
    Custom exception raised to indicate Timestamp errors
    (for example when the end time of the timestamp interval
    is before the start time).
    """


class Timestamp:
    """
    Random generator which when called returns random timestamps in a
    given range.

    """

    def __init__(self, start, end=None, *, fmt='%Y-%m-%d %H:%M:%S', uppercase=False, randgen_offsets=None):
        """
        Initialise timestamp generator.

        Args:
            start (date string):  start time
            end   (date string):  end time (default: current time)
            fmt (str):            formatting string for output (same format as accepted by `datetime.strftime`)
            uppercase (bool):     if True, months are formatted with all uppercase letters (default: False)
            randgen_offsets:      custom random number generator to produce offsets from start time (in seconds)
        """
        # TODO: remove these assert statements and allow start/end to
        # be either datetime objects or strings (which are parsed to
        # create datetime objects).
        assert isinstance(start, str)
        assert isinstance(end, str) or end is None

        self.start = dateutil.parser.parse(start)
        self.end = dt.datetime.now() if end is None else dateutil.parser.parse(end)
        self.dt = int((self.end - self.start).total_seconds())
        self.fmt = fmt
        self.uppercase = uppercase

        if self.dt < 0:
            raise TimestampError("Start time must be before end time. Got: start_time='{}', end_time='{}'."
                                 "".format(self.start, self.end))

        self.randgen = randgen_offsets or RandInt(0, self.dt)

    def next(self):
        """
        Return string representing a random timestamp between `start` and `end`.
        """
        t = self.start + dt.timedelta(seconds=self.randgen.next())
        s = t.strftime(self.fmt)
        return s.upper() if self.uppercase else s

    # [DUPLICATE] seed #6
    def seed(self, seed):
        """
        Initialize random number generator with given seed.
        """
        self.randgen.seed(seed)


class PickFrom:
    """
    Generator which when called returns random elements from a given
    list of choices.

    """

    def __init__(self, values, *, randgen_indices=None):
        """
        Initialise generator.

        Args:
            values (list):    List of options from which to pick elements.
            randgen_indices:  Custom random number generator which determines the
                              indices of chosen elements; should produce integers
                              between 0 (inclusive) and len(values) (exclusive).

        """
        self.values = values
        self.randgen = randgen_indices or RandInt(0, len(self.values) - 1)

    def next(self):
        """
        Return random element from the list of values provided during initialisation.
        """
        idx = self.randgen.next()
        return self.values[idx]

    # [DUPLICATE] seed #8
    def seed(self, seed):
        """
        Initialize random number generator with given seed.
        """
        self.randgen.seed(seed)


class CharString:
    """
    Generator which when called returns strings containing elements
    randomly picked from a set of characters and which have length
    within a specified range.

    """

    def __init__(self, *, chars, length=None, minlength=None, maxlength=None, randgen_lengths=None, randgen_chars=None):
        """
        Initialise character string generator.

        Args:
            chars (list):     list of allowed characters
            length (int):     length of the generated strings (must not be specified
                              simultaneously with minlength/maxlength)
            minlength (int):  minimum length of generated strings
            maxlength (int):  maximum length of generated strings
            randgen_lengths:  custom random number generator which determines
                              the lengths of generated strings
            randgen_chars:    custom random number generator which determines
                              the characters in the generated strings

        """
        self._set_min_and_max_length(length, minlength, maxlength)

        self.chars = chars
        self.rcg = randgen_chars or PickFrom(self.chars)
        self.rlg = randgen_lengths or RandInt(self.minlength, self.maxlength)

    def _set_min_and_max_length(self, length, minlength, maxlength):
        """
        Set min/max length for output strings produced by this generator.

        If `length` is given, it is used as the fixed output length.
        Otherwise `minlength` and `maxlength` are used.

        Raises ValueError if incompatible arguments are provided.

        """
        if length is not None:
            if (minlength is not None or maxlength is not None):
                raise ValueError("Argument `length` must not be given simultaneously with " " `minlength` or `maxlength`.")
            self.minlength = length
            self.maxlength = length
        else:
            if minlength is None:
                minlength = 1
            if maxlength is None:
                raise ValueError("Please specify either `length` or `maxlength`.")

            self.minlength = minlength
            self.maxlength = maxlength

    # [DUPLICATE] seed #9
    def seed(self, seed):
        """
        Initialize random number generator with given seed.
        """
        r = Random(seed)
        length_seed = r.randint(0, 1e18)
        char_seed = r.randint(0, 1e18)
        self.rcg.seed(length_seed)
        self.rlg.seed(char_seed)

    def next(self):
        """
        Return string of random length containing elements randomly picked
        from the list of characters provided during initialisation.

        """
        N = self.rlg.next()
        chars = [self.rcg.next() for _ in range(N)]
        return ''.join(chars)


class DigitString(CharString):
    """
    Generator which when called returns strings containing a sequence
    of random digits and having length within a specified range.

    """

    def __init__(self, **kwargs):
        """
        Initialise generator. All keyword arguments are passed on to
        `CharString`'s initialiser.

        """
        super().__init__(chars='0123456789', **kwargs)


class HashDigest(CharString):
    """
    Generator which when called returns a random hex string representing a hash digest value.

    """

    def __init__(self, **kwargs):
        """
        Initialise generator. All keyword arguments are passed on to
        `CharString`'s initialiser.

        """
        super().__init__(chars='1234567890ABCDEF', **kwargs)
