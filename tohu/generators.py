# -*- coding: utf-8 -*-
"""
Generator classes to produce random data with specific properties.
"""

import datetime as dt
import dateutil
import pandas as pd
import re
import textwrap
from collections import namedtuple
from itertools import count, islice
from mako.template import Template
from random import Random
from tqdm import tqdm

__all__ = [
    'Integer', 'Constant', 'Float', 'Sequential', 'ChooseFrom', 'CharString', 'DigitString', 'HashDigest', 'Geolocation',
    'Timestamp', 'CustomGenerator'
]


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

    def generate(self, N, seed=None):
        """
        Return sequence of `N` elements.

        If `seed` is not None, the generator is reset
        using this seed before generating the elements.
        """
        if seed is not None:
            self.reset(seed)
        yield from islice(self, N)

    def _spawn(self):
        """
        This method needs to be implemented by derived classes.
        It should return a new object of the same type as `self`
        which has the same attributes but is otherwise independent.
        """
        raise NotImplementedError("Class {} does not implement method '_spawn'.".format(self.__class__.__name__))


class Constant(BaseGenerator):
    """
    Generator which produces a constant sequence (repeating the same element indefinitely).
    """

    def __init__(self, value):
        self.value = value

    def _spawn(self):
        return Constant(self.value)

    def reset(self, seed=None):
        pass

    def __next__(self):
        return self.value


class Integer(BaseGenerator):
    """
    Generator which produces random integers k in the range lo <= k <= hi.
    """

    def __init__(self, lo, hi, *, seed=None):
        self.lo = lo
        self.hi = hi
        self.randgen = Random()
        self.reset(seed)

    def _spawn(self):
        return Integer(self.lo, self.hi)

    def reset(self, seed):
        self.randgen.seed(seed)

    def __next__(self):
        return self.randgen.randint(self.lo, self.hi)


class Float(BaseGenerator):
    """
    Generator which produces random floating point numbers x in the range lo <= x <= hi.
    """

    def __init__(self, lo, hi, *, seed=None):
        self.lo = lo
        self.hi = hi
        self.randgen = Random()
        self.reset(seed)

    def _spawn(self):
        return Float(self.lo, self.hi)

    def reset(self, seed):
        self.randgen.seed(seed)

    def __next__(self):
        return self.randgen.uniform(self.lo, self.hi)


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
    """

    def __init__(self, *, prefix, digits):
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


class ChooseFrom(BaseGenerator):
    """
    Generator which produces a sequence of items taken from given a given set of elements.
    """

    def __init__(self, values, *, seed=None):
        """
        Initialise generator.

        Args:
            values (list):    List of options from which to choose elements.
        """
        self.values = values
        self.idxgen = Integer(lo=1, hi=(len(self.values) - 1))
        self.reset(seed)

    def __next__(self):
        """
        Return random element from the list of values provided during initialisation.
        """
        idx = next(self.idxgen)
        return self.values[idx]

    def _spawn(self):
        return ChooseFrom(values=self.values)

    def reset(self, seed):
        self.idxgen.reset(seed)


class CharString(BaseGenerator):
    """
    Generator which produces a sequence of character strings.
    """

    def __init__(self, *, length, chars, seed=None):
        self.length = length
        self.chars = chars
        self.chargen = ChooseFrom(self.chars)
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
        chars = "0123456789ABCDEF"
        self.length = length
        super().__init__(length=length, chars=chars, seed=seed)

    def _spawn(self):
        return HashDigest(length=self.length)


class Geolocation(BaseGenerator):
    """
    Generator which produces a sequence of (lon, lat) coordinates.
    """

    def __init__(self):
        self.lon_gen = Float(-180, 180)
        self.lat_gen = Float(-90, 90)

    def _spawn(self):
        return Geolocation()

    def __next__(self):
        return (next(self.lon_gen), next(self.lat_gen))

    def reset(self, seed):
        self.lon_gen.reset(seed)
        self.lat_gen.reset(seed)


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
            self.end = self.start + dt.timedelta(days=1)
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
        return (self.start + dt.timedelta(seconds=next(self.offsetgen))).strftime(self.fmt)

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


def _create_namedtuple_class(item_cls_name, attrgens):
    item_fields = [name for name in attrgens.keys()]
    return namedtuple(item_cls_name, item_fields)


class ItemCollection:
    def __init__(self, items, N):
        """
        Parameters:
        -----------
        items: iterable
            Sequence of items in the collection.
        N: int
            Number of items in the collection. This needs to be specified explicitly
            because `items` is typically an iterator.
        """
        self.items = list(items)
        self.N = N

    def __iter__(self):
        yield from self.items

    def write(self, filename, *, mode='w', header=None, progressbar=True):
        """
        Export items to a file.

        Arguments:
            filename:     Name of the output file.
            mode:         How to open the file ('w' = write, 'a' = append)
            seed:         If given, reset generator with this seed.
            header:       Header line printed at the very beginning (remember to add a newline at the end).
            progressbar:  Whether to display a progress bar while exporting data.
        """
        assert mode in ['w', 'a', 'write', 'append'], "Argument 'mode' must be either 'w'/'write' or 'a'/'append'."
        assert header is None or isinstance(header, str), "Argument 'header' must be a string."

        with open(filename, mode=mode[0]) as f:
            if header is not None:
                f.write(header)

            for _, x in zip(tqdm(range(self.N)), self.items):
                f.write(format(x))

    def to_df(self):
        return pd.DataFrame([pd.Series(item._asdict()) for item in self.items])


class CustomGeneratorMeta(type):
    def __new__(metacls, cg_name, bases, clsdict):
        gen_cls = super(CustomGeneratorMeta, metacls).__new__(metacls, cg_name, bases, clsdict)
        orig_init = gen_cls.__init__

        def gen_init(self, *args, **kwargs):
            seed = None
            if 'seed' in kwargs:
                seed = kwargs.pop('seed')

            orig_init(self, *args, **kwargs)

            self._attrgens = _create_attribute_generators(self)
            item_cls_name = _get_item_class_name(cg_name)
            self.item_cls = _create_namedtuple_class(item_cls_name, self._attrgens)

            def pprint_item(item):
                s = Template(
                    textwrap.dedent("""
                        <${cls_name}:
                        % for fld in fieldnames:
                            ${fld}: ${getattr(item, fld)}
                        % endfor
                        >
                        """)).render(
                        cls_name=item_cls_name, fieldnames=self.item_cls._fields, item=item)
                print(s)

            # Determine how items produced by this generator should be formatted.
            if not 'FORMAT_STR' in clsdict:
                clsdict['FORMAT_STR'] = ",".join([("${" + fld + "}") for fld in self.item_cls._fields]) + '\n'
                #print("[DDD] Case 1: {} ({})".format(clsdict['FORMAT_STR'], self))
            else:
                # FIXME: This line seems to be called *twice* for every CustomGenerator!!!
                #print("[DDD] Case 2: {} ){})".format(clsdict['FORMAT_STR'], self))
                pass

            self.FORMAT_STR = clsdict['FORMAT_STR']

            def format_obj(obj, fmt):
                return self._formatter.render(**obj._asdict())

            self.item_cls.__format__ = format_obj
            self.item_cls.pprint = pprint_item
            self.item_cls.format = format_obj

            if seed is not None:
                self.reset(seed)

        def gen_get_format_str(self):
            return self._format_str
        def gen_set_format_str(self, format_str):
            self._format_str = format_str
            self._formatter = Template(self._format_str)

        def gen_cls_next(self):
            attrs = {name: next(obj) for name, obj in self._attrgens.items()}
            return self.item_cls(**attrs)

        def gen_reset(self, seed):
            for g in self._attrgens.values():
                g.reset(seed)

        def gen_spawn(self):
            return self.__class__()

        def gen_export(self, filename, *, N, mode='w', seed=None, header=None, progressbar=True):
            """
            Produce `N` elements and write them to the file `f`.

            Arguments:
                filename:     Name of the output file.
                N:            Number of records to write.
                mode:         How to open the file ('w' = write, 'a' = append)
                seed:         If given, reset generator with this seed.
                header:       Header line printed at the very beginning (remember to add a newline at the end).
                progressbar:  Whether to display a progress bar while exporting data.
            """
            item_collection = ItemCollection(self.generate(N, seed=seed), N)
            item_collection.write(filename, mode=mode, header=header, progressbar=progressbar)

        gen_cls.__init__ = gen_init
        gen_cls.__next__ = gen_cls_next
        gen_cls.reset = gen_reset
        gen_cls._spawn = gen_spawn
        gen_cls.export = gen_export
        gen_cls.FORMAT_STR = property(gen_get_format_str, gen_set_format_str)

        return gen_cls


class CustomGenerator(BaseGenerator, metaclass=CustomGeneratorMeta):
    """
    The only purpose of this class is to make defining
    custom generators easier for the user by writing:

        class FooGenerator(CustomGenerator):
            # ...

    instead of the more clumsy:

        class FooGenerator(metaclass=CustomGeneratorMeta):
            # ...
    """

    def generate(self, N, seed=None):
        return ItemCollection(super().generate(N, seed=seed), N)
