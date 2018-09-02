import logging
from .base import DependentGenerator


__all__ = ['IndependentGeneratorMeta', 'ClonedGenerator']

logger = logging.getLogger('tohu')


class TohuCloneError(Exception):
    """
    Custom exception for errors related to cloned generators.
    """


class ClonedGenerator(DependentGenerator):

    def __init__(self, parent):
        self.parent = parent
        self.gen = parent._spawn()

    def __repr__(self):
        return f'<ClonedGenerator: id={id(self)}, parent={self.parent} >'

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
        logger.debug(f'Resetting cloned generator {self} (seed={seed})')
        self.gen.reset(seed)


def attach_new_init_method(cls):
    """
    Replace the existing cls.__init__() method with a new one which
    also initialises the _dependent_generators attribute to an empty list.
    """

    orig_init = cls.__init__

    def new_init(self, *args, **kwargs):
        self._dependent_generators = []
        orig_init(self, *args, **kwargs)

    cls.__init__ = new_init


def attach_new_reset_method(cls):
    """
    Replace existing cls.reset() method with a new one which also
    calls reset() on any clones.
    """
    orig_reset = cls.reset

    def new_reset(self, seed=None):
        orig_reset(self, seed)
        for c in self._dependent_generators:
            c.reset_dependent_generator(seed)
        return self

    cls.reset = new_reset


def attach_make_clone_method(cls):

    def make_clone(self):
        c = ClonedGenerator(parent=self)
        self.register_clone(c)
        return c

    cls.clone = make_clone


def attach_register_clone_method(cls):

    def register_clone(self, clone):
        """
        Register
        """
        assert isinstance(clone, ClonedGenerator), f"Not a cloned generator: {clone}"
        self._dependent_generators.append(clone)

    cls.register_clone = register_clone


class IndependentGeneratorMeta(type):

    def __new__(metacls, cg_name, bases, clsdict):
        new_cls = super(IndependentGeneratorMeta, metacls).__new__(metacls, cg_name, bases, clsdict)

        attach_new_init_method(new_cls)
        attach_new_reset_method(new_cls)
        attach_make_clone_method(new_cls)
        attach_register_clone_method(new_cls)

        return new_cls
