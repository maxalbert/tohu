import logging
import numpy as np
from faker import Faker
from random import Random
from .base_NEW import TohuUltraBaseGenerator
from .derived_generators_NEW import ExtractAttribute

__all__ = ['Constant', 'Integer', 'FakerGenerator', 'SelectOne']

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
        self.values = values
        self.p = p
        self.num_values = len(values)
        self.randgen = np.random.RandomState()

    def spawn(self, dependency_mapping):
        new_instance = SelectOne(self.values, p=self.p)
        new_instance.randgen.set_state(self.randgen.get_state())
        return new_instance

    def __getattr__(self, name):

        if name != '__isabstractmethod__':
            # Special case which is needed because TohuUltraBaseMeta is
            # derived from ABCMeta and it uses '__isabstractmethod__'
            # to check for abstract methods.
            #
            # TODO: This check should probably be moved to TohuUltraBaseGenerator somewhere.
            return

        return ExtractAttribute(self, name)

    def __next__(self):
        """
        Return random element from the list of values provided during initialisation.
        """
        idx = self.randgen.choice(self.num_values, p=self.p)
        return self.values[idx]

    def reset(self, seed):
        if seed is not None:
            self.randgen.seed(seed)
        return self
