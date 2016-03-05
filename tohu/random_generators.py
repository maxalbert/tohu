# -*- coding: utf-8 -*-
"""
Custom random number generators to produce intergers or
floating point numbers in a given interval.

The reason these exist is (i) to be able to set a custom
seed on each new random number generator; (ii) to provide
a convenient interface for the classes in `generators.py`.
"""

from random import Random

# Define a global random number generator which is used
# to generate seeds for the individual random number
# generators in the various classes defined in `randdict`.
# This makes the process of defining dictionaries with
# random fields completely reproducible if desired.
_SEED_GENERATOR = Random()


def new_seed():
    """
    Return new random seed which can be used to initialise
    the random generator in one of the generator classes.
    """
    return _SEED_GENERATOR.randint(0, 1e18)


class RandGenBase:
    """
    Base class for RandInt and RandFloat below.
    """
    random_generator_method = None  # needs to be set in derived classes!

    def __init__(self, a, b, seed=None):
        """
        Initialise random number generator.

        Args:
            a: Lower bound (inclusive) for the sampled values.
            b: Upper bound (inclusive) for the sampled values.

        """
        self.randgen = Random()
        self.randfunc = getattr(self.randgen, self.random_generator_method)
        self.seed(seed or new_seed())
        self.a = a
        self.b = b

    def seed(self, seed):
        """
        Initialize random number generator with given seed.
        """
        self.randgen.seed(seed)

    def next(self):
        """
        Return random number between `a` and `b` (both inclusive).
        """
        return self.randfunc(self.a, self.b)


class RandInt(RandGenBase):
    """
    Random number generator whose `next()` method produces
    a random integer k satisfying a <= k <= b.
    """
    random_generator_method = 'randint'


class RandFloat(RandGenBase):
    """
    Random number generator whose `next()` method produces
    a random float in the interval [a, b].
    """
    random_generator_method = 'uniform'
