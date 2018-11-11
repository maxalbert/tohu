import hashlib
from abc import ABCMeta, abstractmethod
from itertools import islice
from random import Random
from tqdm import tqdm

from .item_list import ItemList
from .logging import logger

__all__ = ['SeedGenerator', 'TohuBaseGenerator']


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

    def _set_random_state_from(self, other):
        self.randgen.setstate(other.randgen.getstate())


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

    def __format__(self, fmt):
        return self.__repr__()

    def set_tohu_name(self, tohu_name):
        """
        Set this generator's `tohu_name` attribute.

        This is mainly useful for debugging where one can temporarily
        use this at the end of generator definitions to set a name
        that will be displayed in debugging messages. For example:

            g1 = SomeGeneratorClass().set_tohu_name('g1')
            g2 = SomeGeneratorClass().set_tohu_name('g2')
        """
        self.tohu_name = tohu_name
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

    def __iter__(self):
        return self

    @abstractmethod
    def reset(self, seed):
        logger.debug(f'Resetting {self} (seed={seed})')
        self.seed_generator.reset(seed)

        # TODO: reset clones once we have added them back in

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

    def _set_random_state_from(self, other):
        self.seed_generator._set_random_state_from(other.seed_generator)

    @abstractmethod
    def spawn(self):
        raise NotImplementedError("Class {} does not implement method 'spawn'.".format(self.__class__.__name__))

