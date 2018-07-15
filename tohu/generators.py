# -*- coding: utf-8 -*-
"""
Generator classes to produce random data with specific properties.
"""

import datetime as dt
import numpy as np
import pandas as pd
import re
import sys
from collections import deque
from faker import Faker
from functools import partial
from itertools import count, islice
from random import Random
from tqdm import tqdm
from .item_collection import ItemCollection
from .item_list import ItemList

__all__ = ['CharString', 'Constant', 'DigitString', 'FakerGenerator', 'First', 'Float', 'Geolocation',
           'GeolocationPair', 'HashDigest', 'Integer', 'Nth', 'NumpyRandomGenerator', 'Second',
           'SeedGenerator', 'SelectMultiple', 'SelectOne', 'Sequential', 'Split', 'Timestamp',
           'TimestampError', 'TupleGenerator', 'Zip']


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

    def generate_OLD(self, N, *, seed=None, progressbar=False):
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
        return ItemCollection(items, N)

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

        return ItemList(item_list, N)

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
        pass

    def __next__(self):
        return self.value


class Integer(BaseGenerator):
    """
    Generator which produces random integers k in the range low <= k <= high.
    """

    def __init__(self, low, high, *, seed=None):
        """
        Parameters
        ----------
        low: integer
            Lower bound (inclusive).
        high: integer
            Upper bound (inclusive).
        seed: integer (optional)
            Seed to initialise this random generator.
        """
        self.low = low
        self.high = high
        self.randgen = Random()
        self.reset(seed)

    def _spawn(self):
        return Integer(self.low, self.high)

    def reset(self, seed):
        self.randgen.seed(seed)

    def __next__(self):
        return self.randgen.randint(self.low, self.high)


class Float(BaseGenerator):
    """
    Generator which produces random floating point numbers x in the range low <= x <= high.
    """

    def __init__(self, low, high, *, seed=None):
        """
        Parameters
        ----------
        low: integer
            Lower bound (inclusive).
        high: integer
            Upper bound (inclusive).
        seed: integer (optional)
            Seed to initialise this random generator.
        """
        self.low = low
        self.high = high
        self.randgen = Random()
        self.reset(seed)

    def _spawn(self):
        return Float(self.low, self.high)

    def reset(self, seed):
        self.randgen.seed(seed)

    def __next__(self):
        return self.randgen.uniform(self.low, self.high)


class NumpyRandomGenerator(BaseGenerator):
    """
    Generator which produces random numbers using one of the methods supported by numpy. [1]

    [1] https://docs.scipy.org/doc/numpy/reference/routines.random.html
    """

    def __init__(self, method, *, seed=None, **numpy_args):
        """
        Parameters
        ----------
        method: string
            Name of the numpy function to use (see [1] for details)
        seed: integer (optional)
            Seed to initialise this random generator
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
        self.reset(seed)

    def _spawn(self):
        return NumpyRandomGenerator(method=self.method, **self.numpy_args)

    def reset(self, seed):
        self.random_state.seed(seed)

    def __next__(self):
        return self.randgen(**self.numpy_args)


class FakerGenerator(BaseGenerator):
    """
    Generator which produces random elements using one of the methods supported by faker. [1]

    [1] https://faker.readthedocs.io/
    """

    def __init__(self, method, *, seed=None, locale=None, **faker_args):
        """
        Parameters
        ----------
        method: string
            Name of the faker provider to use (see [1] for details)
        seed: integer (optional)
            Seed to initialise this random generator
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
        self.reset(seed)

    def _spawn(self):
        return FakerGenerator(method=self.method, locale=self.locale, **self.faker_args)

    def reset(self, seed):
        self.fake.seed(seed)

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

    def __next__(self):
        return self.fmt_str.format(next(self.cnt))


class SelectOne(BaseGenerator):
    """
    Generator which produces a sequence of items taken from given a given set of elements.
    """

    def __init__(self, values, *, seed=None):
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
        self.reset(seed)

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


# Define alias for backwards compatibilty
ChooseFrom = SelectOne


class SelectMultiple(BaseGenerator):
    """
    Generator which produces a sequence of tuples with elements taken from a given set of elements.
    """

    def __init__(self, values, size, *, seed=None):
        """
        Parameters
        ----------
        values: list
            List of options from which to choose elements.
        size: integer
            Size of the output tuples.
        seed: integer (optional)
            Seed to initialise this random generator.
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
        self.reset(seed)

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


class CharString(BaseGenerator):
    """
    Generator which produces a sequence of character strings.
    """

    def __init__(self, *, length, chars, seed=None):
        """
        Parameters
        ----------
        length: integer
            Length of the character strings produced by this generator.
        chars: iterable
            Character set to draw from when generating strings.
        seed: integer (optional)
            Seed to initialise this random generator.
        """
        self.length = length
        self.chars = chars
        self.chargen = SelectOne(self.chars)
        self.reset(seed)

    def __next__(self):
        chars = [next(self.chargen) for _ in range(self.length)]
        return ''.join(chars)

    def reset(self, seed):
        self.chargen.reset(seed)


class DigitString(CharString):
    """
    Generator which produces a sequence of strings containing only digits.
    """

    def __init__(self, *, length, seed=None):
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
        super().__init__(length=length, chars=chars, seed=seed)

    def _spawn(self):
        return DigitString(length=self.length)


class HashDigest(CharString):
    """
    Generator which produces a sequence of hex strings representing hash digest values.
    """

    def __init__(self, *, length, seed=None):
        """
        Parameters
        ----------
        length: int
            Length of the strings produced by this generator.
        seed: integer (optional)
            Seed to initialise this random generator.
        """
        chars = "0123456789ABCDEF"
        self.length = length
        super().__init__(length=length, chars=chars, seed=seed)

    def _spawn(self):
        return HashDigest(length=self.length)


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


# def _create_namedtuple_class(item_cls_name, attrgens):
#     item_fields = [name for name in attrgens.keys()]
#     return namedtuple(item_cls_name, item_fields)


# class ItemCollection:
#     def __init__(self, items, N):
#         """
#         Parameters:
#         -----------
#         items: iterable
#             Sequence of items in the collection.
#         N: int
#             Number of items in the collection. This needs to be specified explicitly
#             because `items` is typically an iterator.
#         """
#         self.items = list(items)
#         self.N = N
#
#     def __repr__(self):
#         return "<ItemCollection of length {}>".format(len(self))
#
#     def __len__(self):
#         return self.N
#
#     def __getitem__(self, i):
#         return self.items[i]
#
#     def __iter__(self):
#         yield from self.items
#
#     def write(self, filename, *, mode='w', header=None, progressbar=True):
#         """
#         Export items to a file.
#
#         Arguments:
#             filename:     Name of the output file.
#             mode:         How to open the file ('w' = write, 'a' = append)
#             header:       Header line printed at the very beginning (remember to add a newline at the end).
#             progressbar:  Whether to display a progress bar while exporting data.
#         """
#         assert mode in ['w', 'a', 'write', 'append'], "Argument 'mode' must be either 'w'/'write' or 'a'/'append'."
#         assert header is None or isinstance(header, str), "Argument 'header' must be a string."
#
#         with open(filename, mode=mode[0]) as f:
#             if header is not None:
#                 f.write(header)
#
#             rng = range(self.N)
#             if progressbar:
#                 rng = tqdm(rng)
#
#             for _, x in zip(rng, self.items):
#                 f.write(format(x))
#
#     def to_df(self):
#         return pd.DataFrame([pd.Series(item._asdict()) for item in self.items])


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


# class CustomGeneratorMeta(type):
#     def __new__(metacls, cg_name, bases, clsdict):
#         gen_cls = super(CustomGeneratorMeta, metacls).__new__(metacls, cg_name, bases, clsdict)
#         orig_init = gen_cls.__init__
#
#         def gen_init(self, *args, **kwargs):
#             seed = None
#             if 'seed' in kwargs:
#                 seed = kwargs.pop('seed')
#
#             orig_init(self, *args, **kwargs)
#
#             self._attrgens = _create_attribute_generators(self)
#             item_cls_name = _get_item_class_name(cg_name)
#             self.item_cls = _create_namedtuple_class(item_cls_name, self._attrgens)
#
#             self._seed_generator = SeedGenerator()
#
#             def pprint_item(item):
#                 s = Template(
#                     textwrap.dedent("""
#                         <${cls_name}:
#                         % for fld in fieldnames:
#                             ${fld}: ${getattr(item, fld)}
#                         % endfor
#                         >
#                         """)).render(
#                         cls_name=item_cls_name, fieldnames=self.item_cls._fields, item=item)
#                 print(s)
#
#             # Determine how items produced by this generator should be formatted.
#             if not 'FORMAT_STR' in clsdict:
#                 clsdict['FORMAT_STR'] = ",".join([("${" + fld + "}") for fld in self.item_cls._fields]) + '\n'
#                 #print("[DDD] Case 1: {} ({})".format(clsdict['FORMAT_STR'], self))
#             else:
#                 # FIXME: This line seems to be called *twice* for every CustomGenerator!!!
#                 #print("[DDD] Case 2: {} ){})".format(clsdict['FORMAT_STR'], self))
#                 pass
#
#             self.FORMAT_STR = clsdict['FORMAT_STR']
#
#             def format_obj(obj, fmt):
#                 return self._formatter.render(**obj._asdict())
#
#             self.item_cls.__format__ = format_obj
#             self.item_cls.pprint = pprint_item
#             self.item_cls.format = format_obj
#
#             if seed is not None:
#                 self.reset(seed)
#
#         def gen_get_format_str(self):
#             return self._format_str
#         def gen_set_format_str(self, format_str):
#             self._format_str = format_str
#             self._formatter = Template(self._format_str)
#
#         def gen_cls_next(self):
#             attrs = {name: next(obj) for name, obj in self._attrgens.items()}
#             return self.item_cls(**attrs)
#
#         def gen_reset(self, seed):
#             # Reset the seed generator
#             self._seed_generator.seed(seed)
#
#             # Reset each constituent generator with a new seed
#             # produced by the seed generator.
#             for g, x in zip(self._attrgens.values(), self._seed_generator):
#                 g.reset(x)
#
#         def gen_spawn(self):
#             return self.__class__()
#
#         def gen_export(self, filename, *, N, mode='w', seed=None, header=None, progressbar=True):
#             """
#             Produce `N` elements and write them to the file `f`.
#
#             Arguments:
#                 filename:     Name of the output file.
#                 N:            Number of records to write.
#                 mode:         How to open the file ('w' = write, 'a' = append)
#                 seed:         If given, reset generator with this seed.
#                 header:       Header line printed at the very beginning (remember to add a newline at the end).
#                 progressbar:  Whether to display a progress bar while exporting data.
#             """
#             item_collection = ItemCollection(self.generate(N, seed=seed), N)
#             item_collection.write(filename, mode=mode, header=header, progressbar=progressbar)
#
#         gen_cls.__init__ = gen_init
#         gen_cls.__next__ = gen_cls_next
#         gen_cls.reset = gen_reset
#         gen_cls._spawn = gen_spawn
#         gen_cls.export = gen_export
#         gen_cls.FORMAT_STR = property(gen_get_format_str, gen_set_format_str)
#
#         return gen_cls
#
#
# class CustomGenerator(BaseGenerator, metaclass=CustomGeneratorMeta):
#     """
#     The only purpose of this class is to make defining
#     custom generators easier for the user by writing:
#
#         class FooGenerator(CustomGenerator):
#             # ...
#
#     instead of the more clumsy:
#
#         class FooGenerator(metaclass=CustomGeneratorMeta):
#             # ...
#     """
#
#     def generate(self, N, *, seed=None, progressbar=False):
#         return ItemCollection(super().generate(N, seed=seed, progressbar=progressbar), N)


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


First = partial(Nth, idx=0)
Second = partial(Nth, idx=1)


# FIXME: Maybe we should remove the `maxbuffer` argument because the way in which `deque`
#        is implemented is that it silently drops elements instead of raising an exception
#        when too many elements are pushed onto the queue?
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
            Maximum number of items to be buffered.
        """
        self.g = g
        self.tuple_len = tuple_len
        self.maxbuffer = maxbuffer
        self._reset_queues()

    def _spawn(self):
        return BufferedTuple(self.g._spawn(), tuple_len=self.tuple_len, maxbuffer=self.maxbuffer)

    def _reset_queues(self):
        self._queues = [deque(maxlen=self.maxbuffer) for _ in range(self.tuple_len)]

    def _refill(self):
        item = next(self.g)
        for x, queue in zip(item, self._queues):
            queue.append(x)

    def reset(self, seed):
        self.g.reset(seed)
        self._reset_queues()

    def next_nth(self, n):
        if len(self._queues[n]) == 0:
            self._refill()
        return self._queues[n].popleft()


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

    class NthElementBuffered(BaseGenerator):
        def __init__(self, g, idx):
            self.g = g
            self.idx = idx

        def __next__(self):
            return self.g.next_nth(self.idx)

        def _spawn(self):
            return NthElementBuffered(self.g._spawn(), self.idx)

        def reset(self, seed):
            self.g.reset(seed)

    return tuple(NthElementBuffered(g_buffered, i) for i in range(tuple_len))


class Zip(TupleGenerator):
    """
    Create a generator which produces tuples that are
    combined from the elements produced by multiple
    individual generators.
    """

    def __init__(self, *generators, seed=None):
        self._generators = [g._spawn() for g in generators]
        self.seed_generator = SeedGenerator()
        self.tuple_len = len(self._generators)
        self.reset(seed)

    def __next__(self):
        return tuple(next(g) for g in self._generators)

    def reset(self, seed):
        self.seed_generator.reset(seed)
        for g in self._generators:
            new_seed = next(self.seed_generator)
            g.reset(new_seed)


def Geolocation():
    """
    Return a pair (Lon, Lat) of iterators producing.
    """
    return Split(GeolocationPair())
