import attr
import datetime as dt
import geojson
import numpy as np
import shapely

from faker import Faker
from random import Random
from shapely.geometry import Point, Polygon, MultiPolygon

from .base import TohuBaseGenerator, PrimitiveGenerator, SeedGenerator
from .logging import logger
from .utils import ensure_is_date_object, ensure_is_datetime_object, identity, make_timestamp_formatter, TohuDateError, TohuTimestampError

__all__ = ['Boolean', 'CharString', 'Constant', 'Date', 'DigitString', 'FakerGenerator', 'Float', 'GeoJSONGeolocation',
           'HashDigest', 'Incremental', 'Integer', 'NumpyRandomGenerator', 'Sequential', 'Timestamp']


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

    @property
    def max_value(self):
        try:
            self.value < self.value
        except TypeError:
             logger.warning(
                 f"The value '{self.value}' of this Constant generator does not support comparison but"
                 "is being asked for its 'max_value'. There may be an error in the logic somewhere."
            )

        return self.value

    def reset(self, seed=None):
        """
        Note that this method supports the `seed` argument (for consistency with other generators),
        but its value is ignored because resetting a Constant generator has no effect.
        """
        super().reset(seed)
        return self

    def __next__(self):
        return self.value

    def spawn(self, spawn_mapping=None):
        return Constant(self.value)

    def _set_random_state_from(self, other):
        pass


class Boolean(PrimitiveGenerator):
    """
    Generator which produces random boolean values (True or False) with a given probability.
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

    def spawn(self, spawn_mapping=None):
        new_obj = Boolean(self.p)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        self.randgen.setstate(other.randgen.getstate())


class Incremental(PrimitiveGenerator):
    """
    Generator which produces integers that increase in regular steps.
    """

    def __init__(self, *, start=0, step=1):
        """
        Parameters
        ----------
        start : int
            Start value of the sequence.
        step : int
            Step size of the sequence.

        Example
        -------
        >>> g = Incremental(start=200, step=4)
        >>> list(g.generate(num=10))
        [200, 204, 208, 212, 216, 220, 224, 228, 232, 236]
        """
        super().__init__()
        self.start = start
        self.step = step
        self.cur_value = start

    def __next__(self):
        retval = self.cur_value
        self.cur_value += self.step
        return retval

    def reset(self, seed=None):
        super().reset(seed)
        self.cur_value = self.start
        return self

    def spawn(self, spawn_mapping=None):
        new_obj = Incremental(start=self.start, step=self.step)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.start = other.start
        self.cur_value = other.cur_value


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

    @property
    def max_value(self):
        return self.high

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

    def spawn(self, spawn_mapping=None):
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

    def spawn(self, spawn_mapping=None):
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

    def spawn(self, spawn_mapping=None):
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

    def spawn(self, spawn_mapping=None):
        new_obj = HashDigest(length=self.length, as_bytes=self.as_bytes, uppercase=self.uppercase)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
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

    def spawn(self, spawn_mapping=None):
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

    def spawn(self, spawn_mapping=None):
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

    def spawn(self, spawn_mapping=None):
        new_obj = FakerGenerator(self.method, locale=self.locale, **self.faker_args)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.fake.random.setstate(other.fake.random.getstate())


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

    def spawn(self, spawn_mapping=None):
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

    def spawn(self, spawn_mapping=None):
        new_obj = GeoJSONGeolocation(self.geojson_data, include_attributes=self.include_attributes, max_tries=self.max_tries)
        new_obj._set_random_state_from(self)
        return new_obj

    def __next__(self):
        sg = self.shape_gen_chooser.choice(self.shape_gens, p=self.choice_probs)
        return next(sg)

    def reset(self, seed):
        super().reset(seed)
        self.shape_gen_chooser.seed(next(self.seed_generator))
        for g in self.shape_gens:
            g.reset(next(self.seed_generator))
        return self

    def _set_random_state_from(self, other):
        self.seed_generator._set_random_state_from(other.seed_generator)
        self.shape_gen_chooser.set_state(other.shape_gen_chooser.get_state())
        for gen_self, gen_other in zip(self.shape_gens, other.shape_gens):
            gen_self._set_random_state_from(gen_other)


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


def get_start_and_end_values(start, end, date):
    if start is not None and end is not None and date is not None:
        raise TohuTimestampError("Arguments 'start', 'end', 'date' must not all be given.")

    if date is None and (start is None or end is None):
        raise TohuTimestampError("If argument 'date' is not given, both 'start' and 'end' must be provided.")

    if date is not None:
        date = ensure_is_date_object(date)

    if start is None:
        start = ensure_is_datetime_object(date)
    else:
        start = ensure_is_datetime_object(start)

    if end is None:
        end = ensure_is_datetime_object(date, optional_offset=dt.timedelta(hours=23, minutes=59, seconds=59))
    else:
        end = ensure_is_datetime_object(end)

    if date is not None:
        if start.date() != date:
            raise TohuTimestampError("Date of start timestamp does not coincide with date argument.")
        if end.date() != date:
            raise TohuTimestampError("Date of end timestamp does not coincide with date argument.")


    return start, end


class Timestamp(TohuBaseGenerator):

    def __init__(self, *, start=None, end=None, date=None, fmt=None, uppercase=None):
        super().__init__()
        self.start, self.end = get_start_and_end_values(start, end, date)
        self.interval = (self.end - self.start).total_seconds()
        self.offset_randgen = Random()
        self._check_start_before_end()

        self.fmt = fmt
        self.uppercase = uppercase
        self._maybe_format_timestamp = make_timestamp_formatter(self.fmt, self.uppercase)

    @property
    def max_value(self):
        return self.end

    def _check_start_before_end(self):
        if self.start > self.end:
            raise TohuTimestampError(f"Start value must be before end value. Got: start={self.start}, end={self.end}")

    def __next__(self):
        offset = self.offset_randgen.randint(0, self.interval)
        ts = self.start + dt.timedelta(seconds=offset)
        return self._maybe_format_timestamp(ts)

    def reset(self, seed):
        super().reset(seed)
        self.offset_randgen.seed(next(self.seed_generator))
        return self

    def spawn(self, spawn_mapping=None):
        new_obj = Timestamp(start=self.start, end=self.end, fmt=self.fmt, uppercase=self.uppercase)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.offset_randgen.setstate(other.offset_randgen.getstate())

    def strftime(self, fmt='%Y-%m-%d %H:%M:%S', uppercase=False):
        g = Timestamp(start=self.start, end=self.end, fmt=fmt, uppercase=uppercase)
        self.register_clone(g)
        g.register_parent(self)
        return g


class Date(TohuBaseGenerator):

    def __init__(self, start, end, *, fmt=None, uppercase=None):
        super().__init__()
        self.start = ensure_is_date_object(start)
        self.end = ensure_is_date_object(end)
        self.interval = (self.end - self.start).days
        self.offset_randgen = Random()
        self._check_start_before_end()

        self.fmt = fmt
        self.uppercase = uppercase
        self._maybe_format_timestamp = make_timestamp_formatter(self.fmt, self.uppercase)

    def _check_start_before_end(self):
        if self.start > self.end:
            raise TohuDateError(f"Start value must be before end value. Got: start={self.start}, end={self.end}")

    def __next__(self):
        offset = self.offset_randgen.randint(0, self.interval)
        ds = self.start + dt.timedelta(days=offset)
        return self._maybe_format_timestamp(ds)

    def reset(self, seed):
        super().reset(seed)
        self.offset_randgen.seed(next(self.seed_generator))
        return self

    def spawn(self, spawn_mapping=None):
        new_obj = Date(self.start, self.end, fmt=self.fmt, uppercase=self.uppercase)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.offset_randgen.setstate(other.offset_randgen.getstate())

    def strftime(self, fmt='%Y-%m-%d', uppercase=False):
        g = Timestamp(start=self.start, end=self.end, fmt=fmt, uppercase=uppercase)
        self.register_clone(g)
        g.register_parent(self)
        return g
