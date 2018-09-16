import logging
from operator import attrgetter
from .base_NEW import TohuUltraBaseGenerator

__all__ = ['ExtractAttribute', 'Lookup']

logger = logging.getLogger('tohu')


class ExtractAttribute(TohuUltraBaseGenerator):
    """
    Generator which produces items that are attributes extracted from
    the items produced by a different generator.
    """

    def __init__(self, g, attr_name):
        logger.debug(f"Extracting attribute '{attr_name}' from parent={g}")
        self.parent = g
        self.gen = g.clone()
        self.attr_name = attr_name
        self.attrgetter = attrgetter(attr_name)

    def __repr__(self):
        return f"<ExtractAttribute '{self.attr_name}' from {self.parent} >"

    def spawn(self, dependency_mapping):

        try:
            new_parent = dependency_mapping[self.parent]
        except KeyError:
            logger.warning(f'ExtractAttribute.spawn():')
            logger.warning(f'   self={self}')
            logger.warning(f'   dependency_mapping={dependency_mapping}')
            raise NotImplementedError("Cannot spawn ExtractAttribute because parent generator is not present in dependency mapping.")

        return ExtractAttribute(new_parent, self.attr_name)

    def clone(self):
        logger.debug('Cloning {self}')
        return ExtractAttribute(self.parent, self.attr_name)

    def __next__(self):
        return self.attrgetter(next(self.gen))

    def reset(self, seed):
        logger.debug(f"Ignoring explicit reset() on derived generator: {self}")

    def reset_clone(self, seed):
        logger.warning("TODO: rename method reset_clone() to reset_dependent_generator() because ExtractAttribute is not a direct clone")
        self.gen.reset(seed)


class Lookup(TohuUltraBaseGenerator):

    def __init__(self, g, mapping):
        self.parent = g
        self.gen = g.clone()
        self.mapping = mapping

    def __next__(self):
        return self.mapping[next(self.gen)]

    def spawn(self, dependency_mapping):
        try:
            new_parent = dependency_mapping[self.parent]
        except KeyError:
            logger.debug(f'While spawning {self}:')
            logger.debug(f'Could not find parent generator in dependency mapping. ')
            logger.debug(f'Using original parent: {self.parent}')
            logger.debug(f'Please check that this is ok.')
            new_parent = self.parent

        return Lookup(new_parent, self.mapping)

    def reset(self, seed):
        logger.debug(f"Ignoring explicit reset() on derived generator: {self}")

    def reset_clone(self, seed):
        logger.warning(
            "TODO: rename method reset_clone() to reset_dependent_generator() because Lookup is not a direct clone")
        self.gen.reset(seed)