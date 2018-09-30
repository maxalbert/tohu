import hashlib

from abc import ABCMeta, abstractmethod
from itertools import islice
from random import Random
from tqdm import tqdm

from .item_list import ItemList
from .logging import logger

__all__ = ['SeedGenerator', 'TohuBaseGenerator']


class TohuBaseGenerator(metaclass=ABCMeta):
    """
    Base class for all of tohu's generators.
    """

    def __init__(self):
        self._clones = []
        self.tohu_name = None

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

    def register_clone(self, clone):
        self._clones.append(clone)

        # If possible, set the clone's tohu_name for easier debugging
        if self.tohu_name is not None:
            clone.set_tohu_name(f"{self.tohu_name} (clone #{len(self._clones)})")

        if len(self._clones) != len(set(self._clones)):
            raise RuntimeError(f"Duplicate clone added: {self}  -->  {clone}")

    @abstractmethod
    def __next__(self):
        raise NotImplementedError("Class {} does not implement method '__next__'.".format(self.__class__.__name__))

    @abstractmethod
    def reset(self, seed):
        logger.debug(f'Resetting {self} (seed={seed})')

        # Print debugging messages in bulk before actually
        # resetting clones because it makes them easier to
        # read in the debugging output.
        if self._clones != []:
            logger.debug('  Will also reset the following clones:')
            for c in self._clones:
                logger.debug(f'   - {c}')

        for c in self._clones:
            c.reset(seed)

    @abstractmethod
    def _set_random_state_from(self, other):
        """
        This helper method sets the internal random state
        of `self` to the same state that `other` is in. This
        ensures that afterwards any the two generators `self`
        and `other` produce the same elements in the same
        order (even though otherwise they remain independent).
        This is used internally when spawning generators.
        """
        raise NotImplementedError("Class {} does not implement method 'spawn'.".format(self.__class__.__name__))

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

    def _set_random_state_from(self, other):
        self.randgen.setstate(other.randgen.getstate())