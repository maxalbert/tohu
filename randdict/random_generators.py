from random import Random


# Define a global random number generator which is used
# to generate seeds for the individual random number
# generators in the various classes defined below.
# This makes the process of defining entities with random
# fields completely reproducible if desired.
_SEED_GENERATOR = Random()


def new_seed():
    """
    Return new random seed which can be used to initialise
    the random generator in one of the generator classes.
    """
    return _SEED_GENERATOR.randint(0, 1e18)



class RandIntGen:
    """
    Random number generator which when called returns
    a random integer k satisfying a <= k <= b.

    """
    def __init__(self, a, b, seed=None):
        """
        Initialise random number generator.

        Args:
            a (int): Lower bound (inclusive) for the sampled values.
            b (int): Upper bound (inclusive) for the sampled values.

        """
        self.randgen = Random()
        self.seed(seed or new_seed())
        self.a = a
        self.b = b

    def next(self):
        """
        Return random integer between `a` and `b` (both inclusive).
        """
        return self.randgen.randint(self.a, self.b)

    # [DUPLICATE] seed #7
    def seed(self, seed):
        """
        Initialize random number generator with given seed.
        """
        self.randgen.seed(seed)


class RandFloatGen:
    """
    Random number generator which when called returns
    a random float in the interval [a, b].

    """
    def __init__(self, a, b, seed=None):
        """
        Initialise random number generator.

        Args:
            a (float): Left endpoint of the sampling interval.
            b (float): Right endpoint of the sampling interval.

        """
        self.randgen = Random()
        self.seed(seed or new_seed())
        self.a = a
        self.b = b

    # [DUPLICATE] seed #4
    def seed(self, seed):
        """
        Initialize random number generator with given seed.
        """
        self.randgen.seed(seed)

    def next(self):
        """
        Return random float in the interval [a, b].
        """
        return self.randgen.uniform(self.a, self.b)
