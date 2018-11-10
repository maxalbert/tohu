import attr
import datetime as dt
import geojson
import numpy as np
import shapely

from faker import Faker
from functools import partial
from random import Random
from shapely.geometry import Point, Polygon, MultiPolygon

from .base import TohuBaseGenerator, SeedGenerator
from .item_list import ItemList
from .logging import logger
from .utils import identity

__all__ = ['Boolean', 'CharString', 'Constant', 'DigitString', 'FakerGenerator', 'Float', 'GeoJSONGeolocation',
           'HashDigest', 'Integer', 'IterateOver', 'NumpyRandomGenerator', 'SelectOnePrimitive',
           'SelectMultiplePrimitive', 'Sequential', 'Timestamp', 'as_tohu_generator']


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
        self.seed_generator = SeedGenerator()
        self.char_gen = Random()

    def spawn(self):
        new_obj = CharString(length=self.length, charset=self.charset)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.seed_generator._set_random_state_from(other.seed_generator)
        self.char_gen.setstate(other.char_gen.getstate())

    def __next__(self):
        chars = self.char_gen.choices(self.charset, k=self.length)
        return ''.join(chars)

    def reset(self, seed):
        super().reset(seed)
        self.seed_generator.reset(seed)
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
        self.randgen.set_state(other.randgen.get_state())


class Sequential(PrimitiveGenerator):
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
        super().__init__()
        self.prefix = prefix
        self.digits = digits
        self.fmt_str = self.prefix + '{{:0{digits}}}'.format(digits=digits)
        self.cnt = 0

    def spawn(self):
        new_obj = Sequential(prefix=self.prefix, digits=self.digits)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.cnt = other.cnt

    def reset(self, seed=None):
        """
        Note that this method supports the `seed` argument (for consistency with other generators),
        but its value is ignored - the generator is simply reset to its initial value.
        """
        super().reset(seed)
        self.cnt = 0
        return self

    def __next__(self):
        self.cnt += 1
        return self.fmt_str.format(self.cnt)


class NumpyRandomGenerator(TohuBaseGenerator):
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
        super().__init__()
        self.method = method
        self.random_state = np.random.RandomState()
        self.randgen = getattr(self.random_state, method)
        self.numpy_args = numpy_args

    def reset(self, seed):
        super().reset(seed)
        self.random_state.seed(seed)
        return self

    def __next__(self):
        return self.randgen(**self.numpy_args)

    def spawn(self):
        new_obj = NumpyRandomGenerator(method=self.method, **self.numpy_args)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.random_state.set_state(other.random_state.get_state())


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


class SelectOnePrimitive(PrimitiveGenerator):
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
        new_obj = SelectOnePrimitive(self.values, p=self.p)
        new_obj._set_random_state_from(self)
        return new_obj


class SelectMultiplePrimitive(PrimitiveGenerator):
    """
    Generator which produces a sequence of items taken from a given set of elements.
    """

    def __init__(self, values, num, p=None):
        """
        Parameters
        ----------
        values: list
            List of options from which to choose elements.
        num: int
            Number of elements to select.
        p: list, optional
            The probabilities associated with each element in `values`.
            If not given the assumes a uniform distribution over all values.
        """
        super().__init__()
        self.values = list(values)  # need to convert to a list so that numpy.random.RandomState() doesn't get confused
        self.num = num
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
            self.func_random_choice = partial(self.randgen.choices, k=self.num)
        else:
            self.randgen = np.random.RandomState()
            self.func_random_choice = partial(self.randgen.choice, p=self.p, k=self.num)

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
        new_obj = SelectMultiplePrimitive(self.values, num=self.num, p=self.p)
        new_obj._set_random_state_from(self)
        return new_obj


def as_tohu_generator(g):
    """
    If g is a tohu generator return it unchanged,
    otherwise wrap it in a Constant generator.
    """

    if isinstance(g, TohuBaseGenerator):
        return g
    else:
        return Constant(g)


class ShapelyGeolocation(PrimitiveGenerator):
    """
    Generator which produces random locations inside a shapely polygon
    or multipolygon. This is a helper class and most users will probably
    find the GeoJSONGeolocation generator more useful.
    """

    def __init__(self, shp, properties=None, max_tries=100):
        if not isinstance(shp, (Polygon, MultiPolygon)):
            raise TypeError(f"Argument 'shp' must be of type Polygon or MultiPolygon. Got: {type(shp)}")

        super().__init__()

        self.shape = shapely.geometry.shape(shp)
        self.properties = properties or dict()

        self.geolocation_cls = self._make_geolocation_class()

        lon_min, lat_min, lon_max, lat_max = self.shape.bounds
        self.lon_gen = Float(lon_min, lon_max)
        self.lat_gen = Float(lat_min, lat_max)
        self.max_tries = max_tries
        self.seed_generator = SeedGenerator()

    def _make_geolocation_class(self):
        fields = {'lon': attr.ib(), 'lat': attr.ib()}
        fields.update({name: attr.ib(value) for name, value in self.properties.items()})
        cls = attr.make_class('Geolocation', fields)
        cls.as_dict = lambda self: attr.asdict(self)
        def __new_eq__(self, other):
            return self.lon == other.lon and self.lat == other.lat
        cls.__eq__ = __new_eq__
        return cls

    def __repr__(self):
        return f"<ShapelyShape, area={self.area:.3f}>"

    def spawn(self):
        new_obj = ShapelyGeolocation(self.shape, properties=self.properties, max_tries=self.max_tries)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.seed_generator._set_random_state_from(other.seed_generator)
        self.lon_gen._set_random_state_from(other.lon_gen)
        self.lat_gen._set_random_state_from(other.lat_gen)

    @property
    def area(self):
        return self.shape.area

    def __next__(self):
        for cnt in range(1, self.max_tries + 1):
            pt = Point(next(self.lon_gen), next(self.lat_gen))
            if pt.within(self.shape):
                return self.geolocation_cls(lon=pt.x, lat=pt.y)
            else:
                logger.debug(f"Generated point is not within shape. Trying again... [{cnt}/{self.max_tries}]")
        raise RuntimeError(f"Could not generate point in shape after {self.max_tries} attempts")

    def reset(self, seed):
        super().reset(seed)
        self.seed_generator.reset(seed)
        self.lon_gen.reset(next(self.seed_generator))
        self.lat_gen.reset(next(self.seed_generator))
        return self


class GeoJSONGeolocation(PrimitiveGenerator):
    """
    Generator which produces random locations inside a geographic area.
    """

    def __init__(self, filename_or_geojson_data, include_attributes=None, max_tries=100):
        super().__init__()

        if isinstance(filename_or_geojson_data, str):
            try:
                with open(filename_or_geojson_data, 'r') as f:
                    geojson_data = geojson.load(f)
            except AttributeError:
                raise NotImplementedError()
        else:
            geojson_data = filename_or_geojson_data

        self.geojson_data = geojson_data
        self.include_attributes = include_attributes or []
        self.max_tries = max_tries

        self.shape_gens = self._make_shape_generators()

        areas = np.array([s.area for s in self.shape_gens])
        self.choice_probs = areas / areas.sum()  # TODO: allow weighin by an arbitrary attribute, not just by area

        self.seed_generator = SeedGenerator()
        self.shape_gen_chooser = np.random.RandomState()

    def _make_shape_generators(self):
        shape_gens = []

        for feature in self.geojson_data['features']:

            geom = shapely.geometry.shape(feature['geometry'])

            cur_attributes = {}
            for name in self.include_attributes:
                try:
                    cur_attributes[name] = feature['properties'][name]
                except KeyError:
                    valid_attributes = list(feature['properties'].keys())
                    raise ValueError(f"Feature does not have attribute '{name}'. Valid attributes are: {valid_attributes}")

            shape_gens.append(ShapelyGeolocation(geom, cur_attributes, max_tries=self.max_tries))

        return shape_gens

    def spawn(self):
        new_obj = GeoJSONGeolocation(self.geojson_data, include_attributes=self.include_attributes, max_tries=self.max_tries)
        new_obj._set_random_state_from(self)
        return new_obj

    def __next__(self):
        sg = self.shape_gen_chooser.choice(self.shape_gens, p=self.choice_probs)
        return next(sg)

    def reset(self, seed):
        super().reset(seed)
        self.seed_generator.reset(seed)
        self.shape_gen_chooser.seed(next(self.seed_generator))
        for g in self.shape_gens:
            g.reset(next(self.seed_generator))

    def _set_random_state_from(self, other):
        self.seed_generator._set_random_state_from(other.seed_generator)
        self.shape_gen_chooser.set_state(other.shape_gen_chooser.get_state())
        for gen_self, gen_other in zip(self.shape_gens, other.shape_gens):
            gen_self._set_random_state_from(gen_other)


class TimestampError(Exception):
    """
    Custom exception raised to indicate Timestamp errors
    (for example when the end time of the timestamp interval
    is before the start time).
    """


class Timestamp(PrimitiveGenerator):
    """
    Generator which produces random timestamps.
    """

    def __init__(self, *, start=None, end=None, date=None, fmt=None, uppercase=False):
        """
        Initialise timestamp generator.

        Note that `start` and `end` are both inclusive. They can either
        be full timestamps such as 'YYYY-MM-DD HH:MM:SS', or date strings
        such as 'YYYY-MM-DD'. Note that in the latter case `end` is
        interpreted as as `YYYY-MM-DD 23:59:59`, i.e. the day is counted
        in full.

        The produced timestamps are datetime objects, but calling
        `strftime(fmt=...)` on this generator another generator is
        returned which produces timestamps as strings instead.

        Alternatively, you can provide the `fmt` argument directly
        to produce timestamps formatted as strings.

        Args:
            start (date string):  start time
            end   (date string):  end time
            date (str):           string of the form YYYY-MM-DD. This is an alternative
                                  (and mutually exclusive) to specifying `start` and `end`.
                                  It is equivalent to setting start='YYYY-MM-DD 00:00:00',
                                  end='YYYY-MM-DD 23:59:59'.
            fmt (str or None):    if given, return timestamps as strings instead of datetime
                                  objects, using `fmt` as the formatting string (default: None)
            uppercase (bool):     whether to format strings as uppercase. If `fmt` is None
                                  then this parameter is ignored.
        """
        super().__init__()

        if (date is not None):
            if not (start is None and end is None):
                raise TimestampError("Argument `date` is mutually exclusive with `start` and `end`.")

            # ensure that date is a string of the form 'YYYY-MM-DD'
            try:
                date = date.strftime('%Y-%m-%d')
            except AttributeError:
                if not isinstance(date, str):
                    raise TypeError("Argument `date` must be either a string or a date-like object "
                                    f"(e.g. datetime.date or pandas.Timestamp). Got: {type(date)}")

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
            raise TimestampError(f"Start time must be before end time. Got: start_time='{self.start}', end_time='{self.end}'.")

        self.fmt = fmt
        self.uppercase = uppercase

        if self.fmt is None:
            self._maybe_format_timestamp = identity
        else:
            if not isinstance(self.fmt, str):
                raise ValueError(f"Argument 'fmt' must be of type string, got '{type(self.fmt)}'")

            if uppercase:
                self._maybe_format_timestamp = lambda ts: ts.strftime(self.fmt).upper()
            else:
                self._maybe_format_timestamp = lambda ts: ts.strftime(self.fmt)

        self.offset_randgen = Random()

    def spawn(self):
        new_obj = Timestamp(start=self.start.strftime('%Y-%m-%d %H:%M:%S'), end=self.end.strftime('%Y-%m-%d %H:%M:%S'),
                            fmt=self.fmt, uppercase=self.uppercase)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.offset_randgen.setstate(other.offset_randgen.getstate())

    def __next__(self):
        next_offset = self.offset_randgen.randint(0, self.dt)
        ts = (self.start + dt.timedelta(seconds=next_offset))
        return self._maybe_format_timestamp(ts)

    def reset(self, seed):
        super().reset(seed)
        self.offset_randgen.seed(seed)
        return self

    def strftime(self, fmt='%Y-%m-%d %H:%M:%S', uppercase=False):
        g = Timestamp(start=self.start.strftime('%Y-%m-%d %H:%M:%S'), end=self.end.strftime('%Y-%m-%d %H:%M:%S'),
                      fmt=fmt, uppercase=uppercase)
        self.register_clone(g)
        return g