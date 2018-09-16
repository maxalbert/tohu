import logging
import numpy as np
from faker import Faker
from random import Random
from .base_NEW import TohuUltraBaseGenerator
from .derived_generators_NEW import ExtractAttribute
from .utils import identity


__all__ = ['Constant', 'HashDigest', 'Integer', 'FakerGenerator', 'SelectOne']

logger = logging.getLogger('tohu')


class Constant(TohuUltraBaseGenerator):
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

    def spawn(self, dependency_mapping):
        return Constant(self.value)

    def reset(self, seed=None):
        return self

    def __next__(self):
        return self.value


class Integer(TohuUltraBaseGenerator):
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

    def spawn(self, dependency_mapping):
        new_instance = Integer(self.low, self.high)
        new_instance.randgen.setstate(self.randgen.getstate())
        return new_instance

    def reset(self, seed):
        self.randgen.seed(seed)
        return self

    def __next__(self):
        return self.randgen.randint(self.low, self.high)


class FakerGenerator(TohuUltraBaseGenerator):
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

    def spawn(self, dependency_mapping):
        new_instance = FakerGenerator(self.method, locale=self.locale, **self.faker_args)
        new_instance.fake.random.setstate(self.fake.random.getstate())
        return new_instance

    def reset(self, seed):
        self.fake.seed_instance(seed)
        return self

    def __next__(self):
        return self.randgen(**self.faker_args)


class SelectOne(TohuUltraBaseGenerator):
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
        self.orig_values = values
        self.parent = self.orig_values if isinstance(self.orig_values, TohuUltraBaseGenerator) else Constant(self.orig_values)
        self.gen = self.parent.clone()
        self.p = p
        self.randgen = np.random.RandomState()

    def spawn(self, dependency_mapping):

        if not isinstance(self.orig_values, TohuUltraBaseGenerator):
            new_values = self.orig_values
        else:
            try:
                # If the original `values` parameter was a tohu generator, check
                # if it was spawned before and if so use it as the new parent.
                new_values = dependency_mapping[self.parent]
            except KeyError:
                logger.debug(f'While spawning {self}:')
                logger.debug(f'Could not find parent generator in dependency mapping. ')
                logger.debug(f'Using original parent: {self.parent}')
                logger.debug(f'Please check that this is ok.')
                new_values = self.orig_values

        new_instance = SelectOne(new_values, p=self.p)
        new_instance.randgen.set_state(self.randgen.get_state())
        return new_instance

    def __getattr__(self, name):

        if name == '__isabstractmethod__':
            # Special case which is needed because TohuUltraBaseMeta is
            # derived from ABCMeta and it uses '__isabstractmethod__'
            # to check for abstract methods.
            #
            # TODO: This check should probably be moved to TohuUltraBaseGenerator somewhere.
            return

        if name == '_ipython_canary_method_should_not_exist_':
            # Special case which is needed because IPython uses this attribute internally.
            raise NotImplementedError("Special case needed for IPython")

        return ExtractAttribute(self, name)

    def __next__(self):
        """
        Return random element from the list of values provided during initialisation.
        """
        cur_values = next(self.gen)
        idx = self.randgen.choice(len(cur_values), p=self.p)
        return cur_values[idx]

    def reset(self, seed):
        logger.debug(f"Ignoring explicit reset() on derived generator: {self}")

    def reset_clone(self, seed):
        logger.warning("TODO: rename method reset_clone() to reset_dependent_generator() because ExtractAttribute is not a direct clone")
        if seed is not None:
            self.randgen.seed(seed)
            #self.gen.reset(seed)
        return self


class HashDigest(TohuUltraBaseGenerator):
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
        if seed is not None:
            self.randgen.seed(seed)

    def __next__(self):
        val = self.randgen.bytes(self._internal_length)
        return self._maybe_convert_to_uppercase(self._maybe_convert_to_hex(val))

    def spawn(self, dependency_mapping):
        new_instance = HashDigest(length=self.length, as_bytes=self.as_bytes, uppercase=self.uppercase)
        new_instance.randgen.set_state(self.randgen.get_state())
        return new_instance
