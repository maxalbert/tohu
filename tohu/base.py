from itertools import islice
from operator import attrgetter
from tqdm import tqdm

from .item_list import ItemList


class UltraBaseGenerator:
    """
    Abstract base class from which every tohu generator is derived
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

    def _spawn(self):
        """
        This method needs to be implemented by derived classes.
        It should return a new object of the same type as `self`
        which has the same attributes but is otherwise independent.
        """
        raise NotImplementedError("Class {} does not implement method '_spawn'.".format(self.__class__.__name__))



class IndependentGenerator(UltraBaseGenerator):
    """
    Abstract base class for independent generators
    """


class DependentGenerator(UltraBaseGenerator):
    """
    Abstract base class for dependent generators
    """


class ExtractAttribute(DependentGenerator):
    """
    Generator which produces items that are attributes extracted from
    the items produced by a different generator.
    """

    def __init__(self, g, attr_name):
        self.parent = g
        self.gen = g._spawn()
        self.attr_name = attr_name
        self.attrgetter = attrgetter(attr_name)

    def __repr__(self):
        return f"<ExtractAttribute '{self.attr_name}' from {self.parent} >"

    def _spawn(self):
        return ExtractAttribute(self.parent, self.attr_name)

    def __next__(self):
        return self.attrgetter(next(self.gen))

    def reset(self, seed):
        self.gen.reset(seed)
