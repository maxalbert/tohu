import hashlib
from abc import ABCMeta, abstractmethod
from itertools import islice
from random import Random
from tqdm import tqdm
from ..item_list import ItemList


class TohuBaseGenerator(metaclass=ABCMeta):
    """
    Base class for all of tohu's generators.
    """

    def __init__(self):
        self._clones = []

    def __repr__(self):
        clsname = self.__class__.__name__
        return f'<{clsname} (id={self.tohu_id})>'

    def __format__(self, fmt):
        clsname = self.__class__.__name__
        return f'<{clsname} (id={self.tohu_id})>'

    @property
    def tohu_id(self):
        """
        Return (truncated) md5 hash representing this generator.
        We truncate the hash simply for readability, as this is
        purely intended for debugging purposes and the risk of
        any collisions will be negligible.
        """
        myhash = hashlib.md5(str(id(self)).encode()).hexdigest()
        return myhash[:12]

    def __iter__(self):
        return self

    def register_clone(self, clone):
        self._clones.append(clone)

    @abstractmethod
    def __next__(self):
        raise NotImplementedError("Class {} does not implement method '__next__'.".format(self.__class__.__name__))

    @abstractmethod
    def reset(self, seed):
        for c in self._clones:
            c.reset(seed)

    @abstractmethod
    def spawn(self):
        raise NotImplementedError("Class {} does not implement method 'spawn'.".format(self.__class__.__name__))

    def clone(self):
        c = self.spawn()
        self.register_clone(c)
        return c

    def generate(self, num, *, seed=None, progressbar=False):
        """
        Return sequence of `num` elements.

        If `seed` is not None, the generator is reset
        using this seed before generating the elements.
        """
        if seed is not None:
            self.reset(seed)

        items = islice(self, num)
        if progressbar:
            items = tqdm(items, total=num)

        item_list = [x for x in items]

        #logger.warning("TODO: initialise ItemList with random seed!")
        return ItemList(item_list, num)


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
