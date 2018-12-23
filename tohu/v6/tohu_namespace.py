from .base import TohuBaseGenerator
from .logging import logger


class TohuNamespaceError:
    """
    Custom exception for TohuNamespace
    """


class TohuNamespace:

    def __init__(self):
        self._ns = {}

    def __len__(self):
        return len(self._ns)

    def __contains__(self, g):
        return g in self._ns.keys()

    @property
    def all_generators(self):
        return self._ns

    def __getitem__(self, key):
        for g, name in self._ns.items():
            if name == key:
                return g
        raise KeyError(f"No generator with name '{key}' exists in this namespace.")

    def __setitem__(self, name, g):
        assert isinstance(g, TohuBaseGenerator)
        if g in self:
            existing_name = self._ns[g]
            if name == existing_name:
                logger.debug(f"Generator already exists with the same name: {g}. Not adding again.")
            else:
                logger.debug("Trying to add existing generator with a different name. Adding a clone instead.")
                self._ns[g.clone()] = name
        else:
            self._ns[g] = name
