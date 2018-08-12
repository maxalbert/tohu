# -*- coding: utf-8 -*-
"""
Generator classes to produce random data with specific properties.
"""

import datetime as dt
import logging
import numpy as np
import re
from faker import Faker
from functools import partial
from itertools import count, islice
from operator import attrgetter
from queue import Queue, Full
from random import Random
from tqdm import tqdm
from .item_list import ItemList

__all__ = ['CharString', 'Constant', 'DigitString', 'ExtractAttribute', 'FakerGenerator', 'First', 'Float', 'Geolocation',
           'GeolocationPair', 'HashDigest', 'Integer', 'IterateOver', 'Nth', 'NumpyRandomGenerator', 'Second',
           'SeedGenerator', 'SelectMultiple', 'SelectOne', 'Sequential', 'Split', 'Timestamp', 'TimestampNEW',
           'TimestampError', 'TupleGenerator', 'Zip']


logger = logging.getLogger("tohu")


# Note: It would be better to make this an abstract base class
#    (to enforce the interface in subclasses) rather than
#    raising NotImplementedError for methods that are not
#    provided by subclasses, but somehow this interferes with
#    the metaclass CustomGeneratorMeta below.
#
class BaseGenerator:
    """
    Base class for all of tohu's random generators.
    """

    def __iter__(self):
        return self

    def __next__(self):
        raise NotImplementedError("Class {} does not implement method '__next__'.".format(self.__class__.__name__))

    def reset(self, seed):
        raise NotImplementedError("Class {} does not implement method 'reset'.".format(self.__class__.__name__))

    def generate_NEW(self, N, *, seed=None, progressbar=False):
        """
        Return sequence of `N` elements.

        If `seed` is not None, the generator is reset
        using this seed before generating the elements.
        """
        if seed is not None:
            self.reset(seed)
        items = islice(self, N)
        if progressbar:
            items = tqdm(items, total=N)

        item_list = [x for x in items]

        #logger.warning("TODO: initialise ItemList with random seed!")
        return ItemList(item_list, N)

    generate = generate_NEW  # alias; to be removed when generate_OLD is removed

    def _spawn(self):
        """
        This method needs to be implemented by derived classes.
        It should return a new object of the same type as `self`
        which has the same attributes but is otherwise independent.
        """
        raise NotImplementedError("Class {} does not implement method '_spawn'.".format(self.__class__.__name__))


class TupleGenerator(BaseGenerator):
    """
    Abstract base class
    """

    @property
    def tuple_len(self):
        """
        Length of tuples produced by this generator.
        """
        try:
            return self._tuple_len
        except AttributeError:
            raise NotImplementedError("Class {} does not implement attribute 'tuple_len'.".format(self.__class__.__name__))

    @tuple_len.setter
    def tuple_len(self, value):
        self._tuple_len = value


class Constant(BaseGenerator):
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

    def _spawn(self):
        return Constant(self.value)

    def reset(self, seed=None):
        return self

    def __next__(self):
        return self.value


class Integer(BaseGenerator):
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

    def _spawn(self):
        return Integer(self.low, self.high)

    def reset(self, seed):
        self.randgen.seed(seed)
        return self

    def __next__(self):
        return self.randgen.randint(self.low, self.high)


class Float(BaseGenerator):
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
        self.low = low
        self.high = high
        self.randgen = Random()

    def _spawn(self):
        return Float(self.low, self.high)

    def reset(self, seed):
        self.randgen.seed(seed)
        return self

    def __next__(self):
        return self.randgen.uniform(self.low, self.high)


class NumpyRandomGenerator(BaseGenerator):
    """
    Generator which produces random numbers using one of the methods supported by numpy. [1]

    [1] https://docs.scipy.org/doc/numpy/reference/routines.random.html
    """

    def __init__(self, method, **numpy_args):
        """
        Parameters
        ----------
        method: string
            Name of the numpy function to use (see [1] for details)
        numpy_args:
            Remaining arguments passed to the numpy function (see [1] for details)

        References
        ----------
        [1] https://docs.scipy.org/doc/numpy/reference/routines.random.html
        """
        self.method = method
        self.random_state = np.random.RandomState()
        self.randgen = getattr(self.random_state, method)
        self.numpy_args = numpy_args

    def _spawn(self):
        return NumpyRandomGenerator(method=self.method, **self.numpy_args)

    def reset(self, seed):
        self.random_state.seed(seed)
        return self

    def __next__(self):
        return self.randgen(**self.numpy_args)


class FakerGenerator(BaseGenerator):
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
        self.method = method
        self.locale = locale
        self.faker_args = faker_args

        self.fake = Faker(locale=locale)
        self.randgen = getattr(self.fake, method)

    def _spawn(self):
        return FakerGenerator(method=self.method, locale=self.locale, **self.faker_args)

    def reset(self, seed):
        self.fake.seed(seed)
        return self

    def __next__(self):
        return self.randgen(**self.faker_args)


class Sequential(BaseGenerator):
    """
    Generator which produces a sequence of strings
    of the form:

        "PREFIX001"
        "PREFIX002"
        "PREFIX003"
        ...

    Both the prefix and the number of digits can
    be modified by the user.

    Example:
        >>> s = Sequential(prefix="Foobar_", digits=4)
        >>> next(s)
        Foobar_0001
        >>> next(s)
        Foobar_0002
        >>> next(s)
        Foobar_0003
    """

    def __init__(self, *, prefix, digits):
        """
        Parameters
        ----------
        prefix: string
            Prefix to be appended to generated elements.
        digits: integer
            Number of digits to use for the sequential numbering.
            Any numbers will fewer digits will be zero-padded;
            numbers with more digits are unaffected.
        """
        self.prefix = prefix
        self.digits = digits
        self.fmt_str = self.prefix + '{{:0{digits}}}'.format(digits=digits)
        self.reset()

    def _spawn(self):
        return Sequential(prefix=self.prefix, digits=self.digits)

    def reset(self, seed=None):
        """
        Note that this method supports the `seed` argument (for consistency with other generators),
        but its value is ignored - the generator is simply reset to its initial value.
        """
        self.cnt = count(start=1)
        return self

    def __next__(self):
        return self.fmt_str.format(next(self.cnt))


class SelectOne(BaseGenerator):
    """
    Generator which produces a sequence of items taken from a given set of elements.
    """

    def __init__(self, values):
        """
        Parameters
        ----------
        values: list
            List of options from which to choose elements.
        seed: integer (optional)
            Seed to initialise this random generator.
        """
        self.values = values
        self.idxgen = Integer(low=0, high=(len(self.values) - 1))

    def __next__(self):
        """
        Return random element from the list of values provided during initialisation.
        """
        idx = next(self.idxgen)
        return self.values[idx]

    def _spawn(self):
        return SelectOne(values=self.values)

    def reset(self, seed):
        self.idxgen.reset(seed)
        return self


# Define alias for backwards compatibilty
ChooseFrom = SelectOne


class SelectMultiple(BaseGenerator):
    """
    Generator which produces a sequence of tuples with elements taken from a given set of elements.
    """

    def __init__(self, values, size):
        """
        Parameters
        ----------
        values: list
            List of options from which to choose elements.
        size: integer
            Size of the output tuples.
        """
        if isinstance(size, int):
            if size < 0:
                raise ValueError(f'Size of output tuples cannot be negative. Got: size={size}')
            size = Integer(low=size, high=size)
        elif not isinstance(size, Integer):
            raise TypeError(f'Argument `size` must be an integer or an Integer generator. Got: size={size} (type: {type(size)})')

        # Note: the chosen implementation is not the most efficient for large values of `size`
        # because we create `size` different SelectOne generators, one for each possible position
        # in the the output tuples. Alternatively, we could just create a single SelectOne
        # generator to produce all output elements. The advantage of multiple generators is
        # that the value of `size` is increased, the first few elements of the output tuples
        # remain the same. This feels nice and consistent, but I'm not sure if this is really
        # necessary (or even desired). In most cases it probably doesn't matter because `size`
        # will typically have a fairly small value.
        self.values = values
        self._size_gen = size
        self._max_size = self._size_gen.high
        self._elem_gens = [SelectOne(values) for _ in range(self._max_size)]
        self._seed_generator = SeedGenerator()

    def __next__(self):
        """
        Return tuple of length `size` with elements drawn from the list of values provided during initialisation.
        """
        cur_size = next(self._size_gen)
        return tuple(next(g) for g in islice(self._elem_gens, cur_size))

    def _spawn(self):
        return SelectMultiple(values=self.values, n=n)

    def reset(self, seed):
        # Reset each individual element generator with a new seed
        self._seed_generator.reset(seed)
        self._size_gen.reset(next(self._seed_generator))
        for g in self._elem_gens:
            elem_seed = next(self._seed_generator)
            g.reset(elem_seed)
        return self


class CharString(BaseGenerator):
    """
    Generator which produces a sequence of character strings.
    """

    def __init__(self, *, length, chars):
        """
        Parameters
        ----------
        length: integer
            Length of the character strings produced by this generator.
        chars: iterable
            Character set to draw from when generating strings.
        """
        self.length = length
        self.chars = chars
        self.chargen = SelectOne(self.chars)

    def __next__(self):
        chars = [next(self.chargen) for _ in range(self.length)]
        return ''.join(chars)

    def reset(self, seed):
        self.chargen.reset(seed)
        return self


class DigitString(CharString):
    """
    Generator which produces a sequence of strings containing only digits.
    """

    def __init__(self, *, length):
        """
        Parameters
        ----------
        length: int
            Length of the digit strings produced by this generator.
        seed: integer (optional)
            Seed to initialise this random generator.
        """
        chars = "0123456789"
        self.length = length
        super().__init__(length=length, chars=chars)

    def _spawn(self):
        return DigitString(length=self.length)


def _identity(x):
    "Helper function which returns its argument unchanged"
    return x


class HashDigest(CharString):
    """
    Generator which produces a sequence of hex strings representing hash digest values.
    """

    def __init__(self, *, length, as_bytes=False):
        """
        Parameters
        ----------
        length: int
            Length of the strings produced by this generator.
        as_bytes: bool
            If True, return byte-string obtained from converting each
            pair of consecutive characters in the hash digest string
            to an ASCII value. Note that in this case `length` must be
            an even number and the actual number of bytes returned in
            each generated hash digest byte string is length/2.
        """
        if as_bytes and (length % 2) != 0:
            raise ValueError(f"Length must be an even number if as_bytes=True (got: length={length})")
        chars = "0123456789ABCDEF"
        self.length = length
        self.as_bytes = as_bytes
        self._maybe_convert_type = bytes.fromhex if self.as_bytes else _identity
        super().__init__(length=length, chars=chars)

    def __next__(self):
        return self._maybe_convert_type(super().__next__())

    def _spawn(self):
        return HashDigest(length=self.length, as_bytes=self.as_bytes)


class GeolocationPair(TupleGenerator):
    """
    Generator which produces a sequence of (lon, lat) coordinates.
    """

    def __init__(self):
        self.lon_gen = Float(-180, 180)
        self.lat_gen = Float(-90, 90)
        self.tuple_len = 2

    def _spawn(self):
        return GeolocationPair()

    def __next__(self):
        return (next(self.lon_gen), next(self.lat_gen))

    def reset(self, seed):
        self.lon_gen.reset(seed)
        self.lat_gen.reset(seed)
        return self


def Geolocation():
    return Split(GeolocationPair())


class TimestampError(Exception):
    """
    Custom exception raised to indicate Timestamp errors
    (for example when the end time of the timestamp interval
    is before the start time).
    """


class Timestamp(BaseGenerator):
    """
    Generator which produces a timestamp.
    """

    def __init__(self, *, start=None, end=None, date=None, fmt='%Y-%m-%d %H:%M:%S', uppercase=False):
        """
        Initialise timestamp generator.

        Note that `start` and `end` are both inclusive. They can either
        be full timestamps such as 'YYYY-MM-DD HH:MM:SS', or date strings
        such as 'YYYY-MM-DD'. Note that in the latter case `end` is
        interpreted as as `YYYY-MM-DD 23:59:59`, i.e. the day is counted
        in full.

        Args:
            start (date string):  start time
            end   (date string):  end time
            date (str):           string of the form YYYY-MM-DD. This is an alternative (and mutually exclusive)
                                  to specifying `start` and `end`.
            fmt (str):            formatting string for output (same format as accepted by `datetime.strftime`)
            uppercase (bool):     if True, months are formatted with all uppercase letters (default: False)
        """
        if (date is not None):
            if not (start is None and end is None):
                raise TimestampError("Argument `date` is mutually exclusive with `start` and `end`.")

            self.start = dt.datetime.strptime(date, '%Y-%m-%d')
            self.end = self.start + dt.timedelta(hours=23, minutes=59, seconds=59)
        else:
            if (start is None or end is None):
                raise TimestampError("Either `date` or both `start` and `end` must be provided.")

            try:
                self.start = dt.datetime.strptime(start, '%Y-%m-%d')
            except ValueError:
                self.start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')

            try:
                self.end = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                end_date = dt.datetime.strptime(end, '%Y-%m-%d')
                self.end = dt.datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)

        self.dt = int((self.end - self.start).total_seconds())
        self.fmt = fmt
        self.uppercase = uppercase

        if self.dt < 0:
            raise TimestampError("Start time must be before end time. Got: start_time='{}', end_time='{}'."
                                 "".format(self.start, self.end))

        self.offsetgen = Integer(0, self.dt)

    def _spawn(self):
        return Timestamp(
            start=self.start.strftime('%Y-%m-%d %H:%M:%S'),
            end=self.end.strftime('%Y-%m-%d %H:%M:%S'),
            fmt=self.fmt,
            uppercase=self.uppercase)

    def __next__(self):
        s = (self.start + dt.timedelta(seconds=next(self.offsetgen))).strftime(self.fmt)
        return s.upper() if self.uppercase else s

    def reset(self, seed):
        self.offsetgen.reset(seed)
        return self


class TimestampNEW(BaseGenerator):
    """
    Generator which produces random timestamps.
    """

    def __init__(self, *, start=None, end=None, date=None):
        """
        Initialise timestamp generator.

        Note that `start` and `end` are both inclusive. They can either
        be full timestamps such as 'YYYY-MM-DD HH:MM:SS', or date strings
        such as 'YYYY-MM-DD'. Note that in the latter case `end` is
        interpreted as as `YYYY-MM-DD 23:59:59`, i.e. the day is counted
        in full.

        Args:
            start (date string):  start time
            end   (date string):  end time
            date (str):           string of the form YYYY-MM-DD. This is an alternative (and mutually exclusive)
                                  to specifying `start` and `end`.
        """
        if (date is not None):
            if not (start is None and end is None):
                raise TimestampError("Argument `date` is mutually exclusive with `start` and `end`.")

            self.start = dt.datetime.strptime(date, '%Y-%m-%d')
            self.end = self.start + dt.timedelta(hours=23, minutes=59, seconds=59)
        else:
            if (start is None or end is None):
                raise TimestampError("Either `date` or both `start` and `end` must be provided.")

            try:
                self.start = dt.datetime.strptime(start, '%Y-%m-%d')
            except ValueError:
                self.start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')

            try:
                self.end = dt.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                end_date = dt.datetime.strptime(end, '%Y-%m-%d')
                self.end = dt.datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)

        self.dt = int((self.end - self.start).total_seconds())

        if self.dt < 0:
            raise TimestampError("Start time must be before end time. Got: start_time='{}', end_time='{}'."
                                 "".format(self.start, self.end))

        self.offsetgen = Integer(0, self.dt)

    def _spawn(self):
        return TimestampNEW(
            start=self.start.strftime('%Y-%m-%d %H:%M:%S'),
            end=self.end.strftime('%Y-%m-%d %H:%M:%S'))

    def __next__(self):
        ts = (self.start + dt.timedelta(seconds=next(self.offsetgen)))
        return ts

    def reset(self, seed):
        self.offsetgen.reset(seed)
        return self



def _create_attribute_generators(custom_generator):
    """
    Scan `custom_generator` for any attributes (both class-level and instance-level))
    which derive from `tohu.generators.BaseGenerator` and return a dictionary
    of the form {attr_name: fresh_generator} containing a freshly spawned
    generator for each of these attributes.
    """
    dict1 = custom_generator.__class__.__dict__
    dict2 = custom_generator.__dict__
    attrgens = {attr_name: obj._spawn() for attr_name, obj in dict1.items() if isinstance(obj, BaseGenerator)}
    attrgens.update({attr_name: obj._spawn() for attr_name, obj in dict2.items() if isinstance(obj, BaseGenerator)})
    return attrgens


def _get_item_class_name(cg_name):
    """
    Return the item name corresponding to the custom generator name `cg_name`.
    This is the "..." part before "...Generator".

    Examples:
        FoobarGenerator -> Foobar
        QuuxGenerator -> Quux
    """
    return re.match('^(.*)Generator$', cg_name).group(1)



class SeedGenerator:
    """
    This class is used in custom generators to create a collection of
    seeds when reset() is called, so that each of the constituent
    generators can be re-initialised with a different seed in a
    reproducible way.

    Note: This is almost identical to the `Integer` class above, but
    we need a version which does *not* inherit from `BaseGenerator`,
    otherwise the automatic item class creation in `CustomGeneratorMeta`
    gets confused.
    """

    def __init__(self):
        self.randgen = Random()
        self.minval = 0
        self.maxval = 2**32-1

    def reset(self, seed):
        self.randgen.seed(seed)

    def __iter__(self):
        return self

    def __next__(self):
        return self.randgen.randint(self.minval, self.maxval)


class Nth(BaseGenerator):
    """
    Generator which allows to extract the n-th element from a tuple-producing generator.
    """

    def __init__(self, g, idx):
        self.g = g
        self.idx = idx

    def __next__(self):
        return next(self.g)[self.idx]

    def _spawn(self):
        return Nth(self.g._spawn(), self.idx)

    def reset(self, seed):
        self.g.reset(seed)
        return self


First = partial(Nth, idx=0)
Second = partial(Nth, idx=1)


class TohuBufferOverflow(Exception):
    """
    Custom exception to indicate a buffer overflow due to a mishandling of linked generators.
    """


class BufferedTuple(BaseGenerator):
    """
    Helper class which allows buffered extraction
    of items from a tuple generator.
    """

    def __init__(self, g, *, tuple_len, maxbuffer=10):
        """
        Parameters
        ----------

        g: tohu generator
            The generator to be buffered. The items produced by `g` must be tuples.
        tuple_len: integer
            Length of tuples produced by g.
        maxbuffer: integer
            Maximum number of items to be buffered. Note that under normal
            circumstances a single buffered element should be sufficient,
            so the default of 10 is probably overcautious. ;)
        """
        self.g = g
        self.tuple_len = tuple_len
        self.maxbuffer = maxbuffer
        self._reset_queues()

    def __repr__(self):
        return f"<BufferedTuple, parent: {self.g}>"

    def _spawn(self):
        raise NotImplementedError("BufferedTuple cannot be spawned directly. Instead, call _spawn_parent() to rewire it to a spawned version of its parent tuple generator.")

    def _spawn_parent(self):
        self.g = self.g._spawn()

    def _reset_queues(self):
        self._queues = [Queue(maxsize=self.maxbuffer) for _ in range(self.tuple_len)]

    def _refill(self):
        item = next(self.g)
        for x, queue in zip(item, self._queues):
            try:
                queue.put_nowait(x)
            except Full:
                raise TohuBufferOverflow("Buffer filled up because elements from multiple linked generators were not consumed at the same rate.")

    def reset(self, seed):
        self.g.reset(seed)
        self._reset_queues()
        return self

    def next_nth(self, n):
        if self._queues[n].empty():
            self._refill()
        return self._queues[n].get()


class InvalidGeneratorError(Exception):
    """
    Custom exception to indicate an instance of NthElementBuffered
    that has been spawned and is therefore invalid.
    """


class NthElementBuffered(BaseGenerator):
    """
    Helper class to iterate over the Nth element in a buffered tuple-generator.
    """

    def __init__(self, g_buffered, idx):
        assert isinstance(g_buffered, BufferedTuple)
        self.g_buffered = g_buffered
        self.idx = idx
        self.invalid = False

    def __repr__(self):
        return f"<NthElementBuffered: idx={self.idx}, parent={self.g_buffered}>"

    def __next__(self):

        if self.invalid:
            # Note: ideally it would be nice to avoid checking a flag every time
            # next() is called to avoid a performance penalty. Originally I tried
            # to invalidate generators by overwriting the __next__ method. However,
            # magic methods are looked up on the class, not the instance (see [1]),
            # so we cannot do this for individual instances.
            #
            # On the other hand, the overhead seems to be on the order of 1.3us per call
            # so this is probably fine.
            #
            # [1] https://stackoverflow.com/questions/33824228/why-wont-dynamically-adding-a-call-method-to-an-instance-work
            raise InvalidGeneratorError("This NthElementBuffered generator has been spawned and is therefore invalid. Please call next() on the spawned version instead.")

        return self.g_buffered.next_nth(self.idx)

    def invalidate(self):
        """
        Invalidate this generator so that it's impossible to call next() on it.
        """
        self.invalid = True

    def _spawn(self):
        logging.debug(
            "Generator of type NthElementBuffered is being spawned. Note that "
            "internally this will spawn its parent, rewire all of the original "
            "parent's children to the new parent and invalidate this generator.")
        self.g_buffered._spawn_parent()
        self.invalidate()
        return NthElementBuffered(self.g_buffered, self.idx)

    def reset(self, seed):
        self.g_buffered.reset(seed)
        return self


def Split(g, *, maxbuffer=10, tuple_len=None):
    """
    Split a tuple generator into individual generators.

    Parameters
    ----------
    g: tohu generator
        The generator to be split. The items produced by `g` must be tuples.
    maxbuffer: integer
        Maximum number of items produced by `g` that will be buffered.
    """
    if tuple_len is None:
        try:
            tuple_len = g.tuple_len
        except AttributeError:
            raise ValueError("Argument 'tuple_len' must be given since generator is not of type TupleGenerator.")

    g_buffered = BufferedTuple(g, maxbuffer=maxbuffer, tuple_len=tuple_len)

    return tuple(NthElementBuffered(g_buffered, i) for i in range(tuple_len))


class Zip(TupleGenerator):
    """
    Create a generator which produces tuples that are
    combined from the elements produced by multiple
    individual generators.
    """

    def __init__(self, *generators):
        self._generators = [g._spawn() for g in generators]
        self.seed_generator = SeedGenerator()
        self.tuple_len = len(self._generators)

    def __next__(self):
        return tuple(next(g) for g in self._generators)

    def reset(self, seed):
        self.seed_generator.reset(seed)
        for g in self._generators:
            new_seed = next(self.seed_generator)
            g.reset(new_seed)
        return self


class IterateOver(BaseGenerator):
    """
    Generator which simply iterates over all items in a given iterable
    """

    def __init__(self, g):
        assert isinstance(g, (list, tuple, ItemList)), \
            "For the time being we enforce g being a list, tuple or ItemList so that we can spawn and reset this generator."
        self.g = g
        self._iter_g = None
        self.reset()

    def __repr__(self):
        return f"<IterateOver, list with {len(self.g)} items>"

    def __next__(self):
        return next(self._iter_g)

    def __iter__(self):
        return self

    def _spawn(self):
        return IterateOver(self.g)

    def reset(self, seed=None):
        self._iter_g = iter(self.g)


class ExtractAttribute(BaseGenerator):
    """
    Generator which produces items that are attributes extracted from
    the items produced by a different generator.
    """

    def __init__(self, g, attr_name):
        self.g = g._spawn()
        self.attr_name = attr_name
        self.attrgetter = attrgetter(attr_name)

    def _spawn(self):
        return ExtractAttribute(self.g, self.attr_name)

    def __iter__(self):
        return self

    def __next__(self):
        return self.attrgetter(next(self.g))

    def reset(self, seed):
        self.g.reset(seed)
