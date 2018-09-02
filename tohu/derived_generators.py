from operator import attrgetter
from .base import logger, DependentGenerator

__all__ = ['ExtractAttribute']


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
        self.parent._dependent_generators.append(self)

    def __repr__(self):
        return f"<ExtractAttribute '{self.attr_name}' from {self.parent} >"

    def _spawn_and_reattach_parent(self, new_parent):
        logger.debug(f'Spawning dependent generator {self} and re-attaching to new parent {new_parent}')
        return ExtractAttribute(new_parent, self.attr_name)

    def __next__(self):
        return self.attrgetter(next(self.gen))

    def reset_dependent_generator(self, seed):
        logger.debug(f'Resetting dependent generator {self} (seed={seed})')
        self.gen.reset(seed)