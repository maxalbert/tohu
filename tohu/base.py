import logging

from itertools import islice
from types import WrapperDescriptorType
from tqdm import tqdm

from .item_list import ItemList

__all__ = ['ClonedGenerator', 'DependentGenerator', 'IndependentGenerator']

logger = logging.getLogger('tohu')


class TohuCloneError(Exception):
    """
    Custom exception for errors related to cloned generators.
    """


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



class DependentGenerator(UltraBaseGenerator):
    """
    Abstract base class for dependent generators
    """
    def reset(self, seed=None):
        logger.debug(f"Ignoring explicit reset() on dependent generator {self}")

    def reset_dependent_generator(self):
        raise NotImplementedError("Class {} does not implement reset_dependent_generator().".format(self.__class__.__name__))

    def _spawn(self):
        raise NotImplementedError("This is a dependent generator. Please call _spawn_and_reattach_parent() instead of _spawn().")

    def _spawn_and_reattach_parent(self, new_parent):
        """
        This method needs to be implemented by derived classes.
        It should return a new object of the same type as `self`
        which has the same attributes but is otherwise independent.
        """
        raise NotImplementedError("Class {} does not implement method '_spawn_and_reattach'.".format(self.__class__.__name__))


class ClonedGenerator(DependentGenerator):

    def __init__(self, parent):
        self.parent = parent
        self.gen = parent._spawn()

    def __repr__(self):
        return f'<ClonedGenerator: id={hex(id(self))}, gen={self.gen}, parent={self.parent} >'

    # def clone(self):
    #     return ClonedGenerator(self.parent)

    def _spawn_and_reattach_parent(self, new_parent):
        logger.debug(f'Spawning cloned generator {self} and re-attaching to new parent {new_parent}')
        return ClonedGenerator(new_parent)

    def __next__(self):
        return next(self.gen)

    def reset(self, seed=None):
        logger.debug(f'Ignoring reset() on cloned generator {self}')

    def reset_dependent_generator(self, seed):
        logger.debug(f'Resetting {self} (seed={seed})')
        self.gen.reset(seed)


def add_new_init_method(cls):
    """
    Replace the existing cls.__init__() method with a new one which
    also initialises the _dependent_generators attribute to an empty list.
    """

    orig_init = cls.__init__

    def new_init(self, *args, **kwargs):
        self._dependent_generators = []
        orig_init(self, *args, **kwargs)

    cls.__init__ = new_init


def add_new_repr_method(cls):
    """
    Add default __repr__ method in case no user-defined one is present.
    """

    if isinstance(cls.__repr__, WrapperDescriptorType):
        cls.__repr__ = lambda self: f"<{self.__class__.__name__}, id={hex(id(self))}>"
    else:
        # Keep the user-defined __repr__ method
        pass



def add_new_reset_method(cls):
    """
    Replace existing cls.reset() method with a new one which also
    calls reset() on any clones.
    """
    orig_reset = cls.reset

    def new_reset(self, seed=None):
        logger.debug(f"Calling reset() on {self} (seed={seed})")
        orig_reset(self, seed)
        for c in self._dependent_generators:
            c.reset_dependent_generator(seed)
        return self

    cls.reset = new_reset


def add_new_clone_method(cls):

    def make_clone(self):
        c = ClonedGenerator(parent=self)
        self.register_clone(c)
        return c

    cls.clone = make_clone


def add_new_register_clone_method(cls):

    def register_clone(self, clone):
        """
        Register
        """
        assert isinstance(clone, ClonedGenerator), f"Not a cloned generator: {clone}"
        self._dependent_generators.append(clone)
        logger.debug(f"Registering new clone: ")
        logger.debug(f"   - parent: {self}")
        logger.debug(f"   - clone: {clone}")
        logger.debug(f"     (total number of dependent generators is now: {len(self._dependent_generators)})")

    cls.register_clone = register_clone


class IndependentGeneratorMeta(type):

    def __new__(metacls, cg_name, bases, clsdict):
        new_cls = super(IndependentGeneratorMeta, metacls).__new__(metacls, cg_name, bases, clsdict)

        add_new_init_method(new_cls)
        add_new_repr_method(new_cls)
        add_new_reset_method(new_cls)
        add_new_clone_method(new_cls)
        add_new_register_clone_method(new_cls)

        return new_cls


class IndependentGenerator(UltraBaseGenerator, metaclass=IndependentGeneratorMeta):
    """
    Abstract base class for independent generators
    """
