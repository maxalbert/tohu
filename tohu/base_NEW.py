from itertools import islice
from random import Random
from tqdm import tqdm

from .item_list import ItemList


class SeedGenerator:
    """
    This class is used in custom generators to create a collection of
    seeds when reset() is called, so that each of the constituent
    generators can be re-initialised with a different seed in a
    reproducible way.

    Note: This is almost identical to the `tohu.Integer` generator, but we
    need a version which does *not* inherit from `TohuUltraBaseGenerator`,
    otherwise the automatic item class creation in `CustomGeneratorMeta`
    gets confused.
    """

    def __init__(self):
        self.randgen = Random()
        self.minval = 0
        self.maxval = 2**32 - 1

    def reset(self, seed):
        self.randgen.seed(seed)

    def __iter__(self):
        return self

    def __next__(self):
        return self.randgen.randint(self.minval, self.maxval)


#
# TODO: Make `TohuUltraBaseGenerator` an abstract base class to ensure that the expected API methods are implemented.
#
class TohuUltraBaseGenerator(metaclass=ABCMeta):
    """
    This is the base class for all tohu generators.
    """

    def __iter__(self):
        return self

    def __next__(self):
        raise NotImplementedError("Class {} does not implement method '__next__'.".format(self.__class__.__name__))

    def reset(self, seed):
        raise NotImplementedError("Class {} does not implement method 'reset'.".format(self.__class__.__name__))

    def generate(self, N, *, seed=None, progressbar=False):
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

        #logger.warning("TODO: initialise ItemList with random seed!")
        return ItemList(item_list, N)
