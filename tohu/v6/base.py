import hashlib

from abc import ABCMeta, abstractmethod
from itertools import islice
from random import Random
from tqdm import tqdm

from .item_list import ItemList
from .logging import logger

__all__ = ['SeedGenerator', 'TohuBaseGenerator', 'PrimitiveGenerator']


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

    def __iter__(self):
        return self

    def __next__(self):
        return self.randgen.randint(self.minval, self.maxval)

    def _set_random_state_from(self, other):
        self.randgen.setstate(other.randgen.getstate())


class TohuCloneError(Exception):
    """
    Custom exception
    """


class TohuBaseGenerator(metaclass=ABCMeta):
    """
    Base class for all of tohu's generators.
    """

    def __init__(self, *args, **kwargs):
        self.tohu_name = None
        self.owner = None
        self.parent = None
        self.clones = []
        self.input_generators = []
        self.seed_generator = SeedGenerator()
        self.is_custom_generator_template = False
        self._max_value = None

    def __repr__(self):
        clsname = self.__class__.__name__
        name = '' if self.tohu_name is None else (f'{self.tohu_name}: ' if not self.is_custom_generator_template else f'{self.tohu_name} (TPL): ')
        owned_by = '' if self.owner is None else f' [owned by: {self.owner}] '
        return f'<{name}{clsname} (id={self.tohu_id}){owned_by}>'

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
    def __next__(self):
        raise NotImplementedError(f"Class {self.__class__.__name__} does not implement method '__next__'.")

    @property
    def max_value(self):
        return self._max_value

    @max_value.setter
    def max_value(self, value):
        if self._max_value is None:
            self._max_value = value
        else:
            if value is not None:
                raise ValueError(f"Trying to set attribute max_value={value} but it already has value {self._max_value}")

    @abstractmethod
    def reset(self, seed):
        """
        Reset this generator's seed generator and any clones.
        """
        logger.debug(f'Resetting {self} (seed={seed})')
        self.seed_generator.reset(seed)

        for c in self.clones:
            c.reset(seed)

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

    @abstractmethod
    def _set_random_state_from(self, other):
        logger.debug(f"Setting internal state of {self} (from {other})")
        self.seed_generator._set_random_state_from(other.seed_generator)

    @abstractmethod
    def spawn(self, spawn_mapping=None):
        raise NotImplementedError("Class {} does not implement method 'spawn'.".format(self.__class__.__name__))

    def clone(self):
        """
        Return an exact copy of this generator which behaves the same way
        (i.e., produces the same elements in the same order) and which is
        automatically reset whenever the original generator is reset.
        """
        c = self.spawn()
        self.register_clone(c)
        c.register_parent(self)
        return c

    def register_clone(self, clone):
        self.clones.append(clone)

        # If possible, set the clone's tohu_name for easier debugging
        if self.tohu_name is not None:
            clone.set_tohu_name(f"{self.tohu_name} (clone #{len(self.clones)})")

        if len(self.clones) != len(set(self.clones)):
            raise RuntimeError(f"Duplicate clone added: {self}  -->  {clone}")

    def unregister_clone(self, clone):
        try:
            self.clones.remove(clone)
        except ValueError:
            raise TohuCloneError(f"Cannot unregister clone {clone} because it is not a clone of parent {self}")

    def register_parent(self, parent):
        self.parent = parent


class PrimitiveGenerator(TohuBaseGenerator):
    """
    Base class for all primitive generators
    """