import hashlib
import logging

from abc import ABCMeta, abstractmethod
from itertools import islice
from random import Random
from tqdm import tqdm

from .item_list import ItemList

logger = logging.getLogger('tohu')


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


def get_init_method_or_empty_placeholder(cls):
    """
    Return the original __init__ method on `cls` if one is defined,
    otherwise return an "empty" __init__ method. (TODO: explain what this means)
    """
    # TODO: return an appropriate "empty" init method if the original class doesn't have one!
    return cls.__init__


class TohuUltraBaseMeta(ABCMeta):

    def __new__(metacls, cg_name, bases, clsdict):
        new_cls = super(TohuUltraBaseMeta, metacls).__new__(metacls, cg_name, bases, clsdict)
        #logger.debug('Inside TohuUltraBaseMeta.__new__()')
        # logger.debug(f'   - metacls={metacls}')
        # logger.debug(f'   - cg_name={cg_name}')
        # logger.debug(f'   - bases={bases}')
        # #logger.debug(f'   - clsdict={clsdict}')
        # logger.debug(f'   - clsdict=<...>')

        orig_init = get_init_method_or_empty_placeholder(new_cls)
        orig_reset = new_cls.reset
        orig_spawn = new_cls.spawn

        def new_init_method(self, *args, **kwargs):
            orig_init(self, *args, **kwargs)
            #logger.debug(f'Inside auto-generated __init__ method for {self}:')

            #logger.debug(f'   - Adding seed_generator')
            self.seed_generator = SeedGenerator()

            #logger.debug(f'   - Initialising _clones to empty list')
            self._clones = []

        def new_reset_method(self, seed=None):
            logger.debug(f'Resetting {self} (seed={seed})')
            orig_reset(self, seed)

            if self._clones != []:
                logger.debug(f'Resetting clones of {self} (using the same seed={seed})')
                for c in self._clones:
                    logger.debug(f'    Automatically resetting {c} (seed={seed})')
                    c.reset_clone(seed)

        def new_spawn_method(self, dependency_mapping):
            if self in dependency_mapping:
                logger.debug(f'{self} was already spawned before. Returning a clone of the previously spawned generator.')
                new_gen = dependency_mapping[self].clone()
            else:
                new_gen = orig_spawn(self, dependency_mapping)

            logger.debug(f'Adding entry to dependency mapping:')
            logger.debug(f'    {self}  -->  {new_gen}')
            dependency_mapping[self] = new_gen
            return new_gen

        new_cls.__init__ = new_init_method
        new_cls.reset = new_reset_method
        new_cls.spawn = new_spawn_method

        return new_cls


class TohuUltraBaseGenerator(metaclass=TohuUltraBaseMeta):
    """
    This is the base class for all tohu generators.
    """
    def __init__(self):
        super().__init__()
        logger.debug('Inside TohuUltraBaseGenerator.__init__')

    def __repr__(self):
        clsname = self.__class__.__name__
        return f'<{clsname} (id={self.tohu_id})>'

    def __format__(self, fmt):
        clsname = self.__class__.__name__
        return f'{clsname} (id={self.tohu_id})'

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
        raise NotImplementedError("Class {} does not implement method '__next__'.".format(self.__class__.__name__))

    @abstractmethod
    def reset(self, seed):
        raise NotImplementedError("Class {} does not implement method 'reset'.".format(self.__class__.__name__))

    @abstractmethod
    def spawn(self, dependency_mapping):
        raise NotImplementedError("Class {} does not implement method 'spawn'.".format(self.__class__.__name__))

    def clone(self):
        c = ClonedGenerator(self)
        self._clones.append(c)
        return c

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


class ClonedGenerator(TohuUltraBaseGenerator):

    def __init__(self, parent):
        self.parent = parent
        self.gen = parent.spawn(dependency_mapping=dict())

    def __format__(self, fmt):
        if fmt == 'long':
            return f'ClonedGenerator(parent={self.parent}) (id={self.tohu_id})'
        elif fmt == '' or fmt == 'short':
            return f'ClonedGenerator (id={self.tohu_id})'
        else:
            raise ValueError(f"Invalid format spec: '{fmt}'. Valid values are: 'short', 'long'")

    def __next__(self):
        return next(self.gen)

    def reset(self, seed):
        logger.debug(f"Ignoring explicit reset() on cloned generator: {self}")

    def reset_clone(self, seed):
        self.gen.reset(seed)

    def clone(self):
        return self.parent.clone()

    def spawn(self, dependency_mapping):
        if self.parent in dependency_mapping:
            return dependency_mapping[self.parent].clone()
        else:
            raise NotImplementedError("Cannot currently spawn a ClonedGenerator whose parent is not in the dependency mapping")
