import datetime as dt
import pandas as pd

from random import Random

from .base import TohuBaseGenerator, SeedGenerator
from .primitive_generators import as_tohu_generator, Constant
from .spawn_mapping import SpawnMapping
from .utils import parse_datetime_string, TohuTimestampError

__all__ = ['Apply', 'Lookup', 'SelectMultiple', 'SelectOne', 'Timestamp']


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


class Apply(DerivedGenerator):
    """
    Generator which applies a callable to a elements produced by a set of input generators.
    """

    def __init__(self, callable, *arg_gens, **kwarg_gens):
        super().__init__()
        self.callable = callable
        self.arg_gens_orig = arg_gens
        self.kwarg_gens_orig = kwarg_gens

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

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_arg_gens_orig = [spawn_mapping[g] for g in self.arg_gens_orig]
        new_kwarg_gens_orig = {name: spawn_mapping[g] for name, g in self.kwarg_gens_orig}
        new_obj = Apply(self.callable, *new_arg_gens_orig, **new_kwarg_gens_orig)
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
        return Apply(get_size, self)


def as_tohu_timestamp_generator(x, optional_offset=None):
    """
    Helper function which ensures that the returned

    Allowed input types:

      - datetime string of the form "YYYY-MM-DD HH:MM:SS"
      - date string of the form "YYYY-MM-DD"
      - datetime.datetime object
      - pandas.Timestamp object
      - tohu generator which

    The argument `optional_offset`
    """
    if isinstance(x, str):
        ts = parse_datetime_string(x, optional_offset)
        return as_tohu_generator(ts)
    elif isinstance(x, dt.datetime):
        return as_tohu_generator(x)
    elif isinstance(x, pd.Timestamp):
        return as_tohu_generator(x.to_pydatetime())
    elif isinstance(x, TohuBaseGenerator):
        if isinstance(x, Timestamp):
            return x
        elif isinstance(x, Constant):
            if isinstance(x.value, dt.datetime):
               return x
            else:
                raise ValueError(f"If input is a Constant tohu generator, its return value "
                                 f"must be of type datetime.datetime. Got: '{type(x.value)}'")
        else:
            raise TypeError(f"If input is a tohu generator it must be of type 'Timestamp' or 'Constant'. Got: '{type(x)}'")
    else:
        raise ValueError(f"Cannot convert input argument to timestamp: {x}")


def get_earliest_value(g):
    if isinstance(g, Constant):
        return g.value
    elif isinstance(g, Timestamp):
        return get_earliest_value(g.start_gen)
    else:
        raise TypeError("This should not occur.")


def get_latest_value(g):
    if isinstance(g, Constant):
        return g.value
    elif isinstance(g, Timestamp):
        return get_latest_value(g.end_gen)
    else:
        raise TypeError("This should not occur.")


def check_start_before_end(start_gen, end_gen):
    latest_start_value = get_latest_value(start_gen)
    earliest_end_value = get_earliest_value(end_gen)

    if latest_start_value > earliest_end_value:
        error_msg = (
            "Latest start value must be before earliest end value. "
            f"Got: latest start value: {latest_start_value}, earliest end value: {earliest_end_value}"
        )
        raise TohuTimestampError(error_msg)


class Timestamp(Apply):

    def __init__(self, *, start=None, end=None, date=None):
        self.start_gen = as_tohu_timestamp_generator(start)
        self.end_gen = as_tohu_timestamp_generator(end, optional_offset=dt.timedelta(hours=23, minutes=59, seconds=59))
        check_start_before_end(self.start_gen, self.end_gen)
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

    def reset(self, seed):
        super().reset(seed)
        self.offset_randgen.seed(next(self.seed_generator))

    def spawn(self, spawn_mapping=None):
        spawn_mapping = spawn_mapping or SpawnMapping()
        new_obj = Timestamp(spawn_mapping[self.start_gen], spawn_mapping[self.end_gen])
        new_obj._set_random_state_from(self)
        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.offset_randgen.setstate(other.offset_randgen.getstate())

    def strftime(self, fmt):
        func = lambda x: x.strftime(fmt)
        return Apply(func, self)
