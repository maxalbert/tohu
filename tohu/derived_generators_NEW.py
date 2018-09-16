import logging
from operator import attrgetter
from .base_NEW import TohuUltraBaseGenerator

__all__ = ['ExtractAttribute']

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
        logger.warning(f'ExtractAttribute.spawn(): dependency_mapping={dependency_mapping}')
        raise NotImplementedError()

    def __next__(self):
        return self.attrgetter(next(self.gen))
