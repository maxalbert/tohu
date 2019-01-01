import datetime as dt

from random import Random

from .base import TohuBaseGenerator, SeedGenerator
from .logging import logger
from .primitive_generators import as_tohu_generator, Constant, Date, Timestamp as TimestampPrimitive
from .spawn_mapping import SpawnMapping
from .utils import TohuDateError, TohuTimestampError, ensure_is_date_object, make_timestamp_formatter

__all__ = ['Apply', 'Integer', 'Lookup', 'SelectMultiple', 'SelectOne', 'Tee', 'Timestamp']


class DerivedGenerator(TohuBaseGenerator):
    """
    Base class for all derived generators
    """

    def reset_input_generators(self, seed):
        """
        Helper method which explicitly resets all input generators
        to the derived generator. This should only ever be called
        for testing or debugging.
        """
        seed_generator = SeedGenerator().reset(seed=seed)

        for gen in self.input_generators:
            gen.reset(next(seed_generator))
            try:
                # In case `gen` is itself a derived generator,
                # recursively reset its own input generators.
                gen.reset_input_generators(next(seed_generator))
            except AttributeError:
                pass


class Apply(DerivedGenerator):
    """
    Generator which applies a callable to a elements produced by a set of input generators.
    """

    def __init__(self, callable, *arg_gens, max_value=None, **kwarg_gens):
        super().__init__()
        self.callable = callable
        self.arg_gens_orig = arg_gens
        self.kwarg_gens_orig = kwarg_gens
        self.max_value = max_value

        self.arg_gens = [g.clone() for g in self.arg_gens_orig]
        self.kwarg_gens = {name: g.clone() for name, g in self.kwarg_gens_orig.items()}
        self.input_generators = [g for g in self.arg_gens_orig] + [g for g in self.kwarg_gens_orig.values()]
        self.constituent_generators = [g for g in self.arg_gens] + [g for g in self.kwarg_gens.values()]
        for gen in self.constituent_generators:
            gen.owner = self

    def __next__(self):
        args = [next(g) for g in self.arg_gens]
        kwargs = {name: next(g) for name, g in self.kwarg_gens.items()}
        return self.callable(*args, **kwargs)

    def reset(self, seed):
        super().reset(seed)

        try:
            self.callable.reset(next(self.seed_generator))
        except AttributeError:
            logger.debug(
                f"Failed to reset callable in generator {self}. Assuming that "
                "it does not contain any random generators that need resetting."
            )

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_arg_gens_orig = [spawn_mapping[g] for g in self.arg_gens_orig]
        new_kwarg_gens_orig = {name: spawn_mapping[g] for name, g in self.kwarg_gens_orig}
        new_obj = Apply(self.callable, *new_arg_gens_orig, max_value=self.max_value, **new_kwarg_gens_orig)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        for g_self, g_other in zip(self.constituent_generators, other.constituent_generators):
            g_self._set_random_state_from(g_other)


class Lookup(Apply):
    """
    Generator which performs a lookup of elements produced by another generator.
    """

    def __init__(self, key, mapping):
        self.key = as_tohu_generator(key)
        self.mapping = as_tohu_generator(mapping)

        def f_lookup(key, mapping):
            return mapping[key]

        super().__init__(f_lookup, self.key, self.mapping)

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_obj = Lookup(spawn_mapping[self.key], spawn_mapping[self.mapping])
        new_obj._set_random_state_from(self)
        return new_obj


class Integer(Apply):

    def __init__(self, low, high):
        self.low_gen = as_tohu_generator(low)
        self.high_gen = as_tohu_generator(high)
        self.randgen = Random()
        super().__init__(self.randgen.randint, self.low_gen, self.high_gen)
        self.max_value = self.high_gen.max_value

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(next(self.seed_generator))

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_obj = Integer(spawn_mapping[self.low_gen], spawn_mapping[self.high_gen])
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())


class SelectOne(Apply):
    """
    Generator which selects a single element from each sequence produced by another generator.
    """

    def __init__(self, values):
        self.values_gen = as_tohu_generator(values)
        self.randgen = Random()
        func = self.randgen.choice
        super().__init__(func, self.values_gen)

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_obj = SelectOne(spawn_mapping[self.values_gen])
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())



class SelectMultiple(Apply):
    """
    Generator which selects multiple elements (without replacement)
    from each sequence produced by another generator.
    """

    def __init__(self, values, num):
        self.values_gen = as_tohu_generator(values)
        self.num_gen = as_tohu_generator(num)
        self.randgen = Random()
        func = self.randgen.sample
        super().__init__(func, self.values_gen, k=self.num_gen)

    def reset(self, seed):
        super().reset(seed)
        self.randgen.seed(seed)

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_obj = SelectMultiple(spawn_mapping[self.values_gen], spawn_mapping[self.num_gen])
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.randgen.setstate(other.randgen.getstate())

    def size(self):
        def get_size(x):
            return len(x)
        g = Apply(get_size, self, max_value=self.num_gen.max_value)
        return g


class Tee(Apply):

    def __init__(self, g, num):
        self.g_orig = g
        self.num_gen = as_tohu_generator(num)

        if self.num_gen.max_value > 1000:
            raise NotImplementedError(
                "This Tee generator is intended to be used to produce small-ish output tuples. "
                "The current implementation is not ideal for potentially large tuples, which"
                "which is why we only allow sizes up to 1000 elements at the moment."
            )

        def make_tuple(num, *values):
            return tuple(values[:num])

        value_gens = [g.spawn() for _ in range(self.num_gen.max_value)]
        super().__init__(make_tuple, self.num_gen, *value_gens)


def convert_to_date_object(date):
    if isinstance(date, Constant):
        return convert_to_date_object(date.value)
    elif isinstance(date, Date) and date.start == date.end:
        return date.start
    else:
        try:
            return ensure_is_date_object(date)
        except TohuDateError:
            raise TohuTimestampError(f"Argument 'date' must represent some kind of constant date object. Got: {date}")


def get_start_generator(start, date):
    if date is not None:
        date = convert_to_date_object(date)

    if start is None:
        start_value = dt.datetime(date.year, date.month, date.day)
        start_gen = Constant(start_value)
    elif isinstance(start, str):
        start_value = dt.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        start_gen = Constant(start_value)
    elif isinstance(start, dt.datetime):
        return Constant(start)
    elif isinstance(start, Constant):
        return get_start_generator(start.value, date)
    elif isinstance(start, TimestampPrimitive):
        # Create a new generator to strip any string formatting information in case it exists
        start_without_formatting = TimestampPrimitive(start=start.start, end=start.end)
        start.register_clone(start_without_formatting)
        start_without_formatting.register_parent(start)
        return start_without_formatting
    else:
        raise NotImplementedError()

    return start_gen


def get_end_generator(end, date):
    if date is not None:
        date = convert_to_date_object(date)

    if end is None:
        end_value = dt.datetime(date.year, date.month, date.day, 23, 59, 59)
        end_gen = Constant(end_value)
    elif isinstance(end, str):
        end_value = dt.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        end_gen = Constant(end_value)
    elif isinstance(end, dt.datetime):
        return Constant(end)
    elif isinstance(end, Constant):
        return get_start_generator(end.value, date)
    elif isinstance(end, TimestampPrimitive):
        # Create a new generator to strip any string formatting information in case it exists
        end_without_formatting = TimestampPrimitive(start=end.start, end=end.end)
        end.register_clone(end_without_formatting)
        end_without_formatting.register_parent(end)
        return end_without_formatting
    else:
        raise NotImplementedError()

    return end_gen


def get_start_end_end_generator(start, end, date):
    start_gen = get_start_generator(start, date)
    end_gen = get_end_generator(end, date)
    return start_gen, end_gen


def check_valid_inputs(start_gen, end_gen, date):
    if date is not None:
        date = convert_to_date_object(date)

    if date is not None:
        if isinstance(start_gen, TimestampPrimitive):
            if not (start_gen.start.date() == date and start_gen.end.date() == date):
                raise TohuTimestampError(
                    "If the 'date' argument is given, all possible 'start' timestamp values must lie on that given date."
                )
        if isinstance(end_gen, TimestampPrimitive):
            if not (end_gen.start.date() == date and end_gen.end.date() == date):
                raise TohuTimestampError(
                    "If the 'date' argument is given, all possible 'end' timestamp values must lie on that given date."
                )

    start_end_error_msg = (
        "Latest possible value of 'start' generator must not be after "
        "earliest possible value of 'end' generator."
    )

    if isinstance(start_gen, TimestampPrimitive) and isinstance(end_gen, TimestampPrimitive):
        if start_gen.end > end_gen.start:
            raise TohuTimestampError(start_end_error_msg)
    elif isinstance(start_gen, TimestampPrimitive) and isinstance(end_gen, Constant):
        if start_gen.end > end_gen.value:
            raise TohuTimestampError(start_end_error_msg)
    elif isinstance(start_gen, Constant) and isinstance(end_gen, TimestampPrimitive):
        if start_gen.value > end_gen.start:
            raise TohuTimestampError(start_end_error_msg)
    elif isinstance(start_gen, Constant) and isinstance(end_gen, Constant):
        if start_gen.value> end_gen.value:
            raise TohuTimestampError("Start value must be before end value. Got: start={self.start}, end={self.end}")


class Timestamp(Apply):

    def __init__(self, *, start=None, end=None, date=None, fmt=None, uppercase=None):

        if start is None and end is None and date is None:
            raise TohuTimestampError("Not all input arguments can be None.")

        if start is not None and end is not None and date is not None:
            raise TohuTimestampError("Arguments 'start', 'end', 'date' cannot all be provided.")

        self.start_gen, self.end_gen = get_start_end_end_generator(start, end, date)
        check_valid_inputs(self.start_gen, self.end_gen, date)

        self.offset_randgen = Random()

        def func(start, end):
            interval = (end - start).total_seconds()
            try:
                offset = self.offset_randgen.randint(0, interval)
            except ValueError:
                raise TohuTimestampError(f"Start generator produced timestamp later than end generator: start={start}, end={end}")
            ts = (start + dt.timedelta(seconds=offset))
            return ts

        super().__init__(func, self.start_gen, self.end_gen)

        self.max_value = self.end_gen.max_value

        self.fmt = fmt
        self.uppercase = uppercase
        self._maybe_format_timestamp = make_timestamp_formatter(self.fmt, self.uppercase)

    def __next__(self):
        ts = super().__next__()
        return self._maybe_format_timestamp(ts)

    def reset(self, seed):
        super().reset(seed)
        self.offset_randgen.seed(next(self.seed_generator))
        return self

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_obj = Timestamp(start=spawn_mapping[self.start_gen], end=spawn_mapping[self.end_gen], fmt=self.fmt, uppercase=self.uppercase)
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.offset_randgen.setstate(other.offset_randgen.getstate())

    def strftime(self, fmt='%Y-%m-%d %H:%M:%S', uppercase=False):
        g = Timestamp(start=self.start_gen, end=self.end_gen, fmt=fmt, uppercase=uppercase)
        self.register_clone(g)
        g.register_parent(self)
        return g
