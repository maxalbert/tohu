import hashlib
from abc import ABCMeta, abstractmethod
from itertools import islice
from random import Random
from tqdm import tqdm

from .item_list import ItemList
from .logging import logger

__all__ = ['SeedGenerator', 'TohuBaseGenerator']


class TohuCloneError(Exception):
    """
    Custom exception
    """


class SpawnMapping:

    def __init__(self):
        self.mapping = {}

    def add_mapping(self, g, g_spawned):
        self.mapping[g] = g_spawned

    def __contains__(self, item):
        return item in self.mapping

    def __getitem__(self, key):
        return self.mapping[key]


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
        self.parent = None
        self._clones = []
        self._input_generators = []
        self._constituent_generators = []
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
        """
        Reset this generator's seed generator and any clones.
        """
        logger.debug(f'Resetting {self} (seed={seed})')
        self.seed_generator.reset(seed)

        for c in self._clones:
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

    def _set_random_state_from(self, other):
        self.seed_generator._set_random_state_from(other.seed_generator)

    def spawn(self, spawn_mapping=None):
        """
        Return an exact copy of this generator which behaves the same way
        (i.e., produces the same elements in the same order) but is otherwise
        independent, i.e. there is no link between the two generators
        (as opposed to a cloned generator, which is automatically reset
        whenever the original generator is reset).
        """
        spawn_mapping = spawn_mapping or SpawnMapping()

        if self.parent is not None:
            if self.parent in spawn_mapping:
                # Return new clone of the mapped parent
                return spawn_mapping[self.parent].clone()
            else:
                raise TohuCloneError("Cannot spawn a cloned generator without being able to map its parent.")
        else:
            new_obj = self._spawn(spawn_mapping)
            spawn_mapping.add_mapping(self, new_obj)
            return new_obj

    @abstractmethod
    def _spawn(self, spawn_mapping):
        raise NotImplementedError("Class {} does not implement method '_spawn'.".format(self.__class__.__name__))

    def clone(self, spawn_mapping=None):
        """
        Return an exact copy of this generator which behaves the same way
        (i.e., produces the same elements in the same order) and which is
        automatically reset whenever the original generator is reset.
        """
        c = self.spawn(spawn_mapping)
        self.register_clone(c)
        c.register_parent(self)
        return c

    def register_clone(self, clone):
        self._clones.append(clone)

        # If possible, set the clone's tohu_name for easier debugging
        if self.tohu_name is not None:
            clone.set_tohu_name(f"{self.tohu_name} (clone #{len(self._clones)})")

        if len(self._clones) != len(set(self._clones)):
            raise RuntimeError(f"Duplicate clone added: {self}  -->  {clone}")

    def register_parent(self, parent):
        self.parent = parent

    @property
    def parent_chain(self):
        n = self.parent
        chain = []
        while n:
            chain.append(n)
            n = n.parent
        return chain
