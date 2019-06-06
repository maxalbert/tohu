import hashlib
from abc import ABCMeta, abstractmethod
from itertools import islice
from random import Random
from tqdm import tqdm

from .item_list import ItemList
from .logging import logger

__all__ = ["TohuBaseGenerator", "PrimitiveGenerator"]


class SeedGenerator:
    """
    This class is used in custom generators to create a collection of
    seeds when reset() is called, so that each of the constituent
    generators can be re-initialised with a different seed in a
    reproducible way.

    Note: This is almost identical to the `tohu.Integer` generator, but we
    need a version which does *not* inherit from `TohuBaseGenerator`,
    otherwise the automatic item class creation in custom generators
    gets confused.
    """

    def __init__(self):
        self.randgen = Random()
        self.minval = 0
        self.maxval = 2**32 - 1

    def reset(self, seed):
        self.randgen.seed(seed)
        return self

    # def __next__(self):
    #     return self.randgen.randint(self.minval, self.maxval)
    #
    # def _set_state_from(self, other):
    #     self.randgen.setstate(other.randgen.getstate())


class TohuBaseGenerator(metaclass=ABCMeta):
    """
    Base class for all of tohu's generators.
    """

    def __init__(self):
        self.tohu_name = None
        self.seed_generator = SeedGenerator()

    def __repr__(self):
        clsname = self.__class__.__name__
        name = '' if self.tohu_name is None else f'{self.tohu_name}: '
        return f'<{name}{clsname} (id={self.tohu_id})>'

    def __iter__(self):
        return self

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

    @abstractmethod
    def reset(self, seed):
        """
        Reset this generator's seed generator and any clones.
        """
        logger.debug(f'Resetting {self} (seed={seed})')
        self.seed_generator.reset(seed)
        #
        # for c in self.clones:
        #     c.reset(seed)

    def generate(self, num, *, seed=None, progressbar=False):
        """
        Return sequence of `num` elements.

        If `seed` is not None, the generator is reset
        using this seed before generating the elements.
        """
        if seed is not None:
            self.reset(seed)

        items = islice(self, num)
        if progressbar:  # pragma: no cover
            items = tqdm(items, total=num)

        item_list = [x for x in items]
        return ItemList(item_list)


class PrimitiveGenerator(TohuBaseGenerator):
    """
    Base class for all primitive generators
    """
