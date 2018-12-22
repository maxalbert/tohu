from bidict import bidict

from .base import TohuBaseGenerator
from .logging import logger


class TohuNamespaceError(Exception):
    pass


class TohuNamespace:

    def __init__(self):
        # _gens2names is a dict with entries of the form {generator -> name} (includes anonymous generators)
        # _names2gens is a dict with entries of the form {name -> generator} (excludes anonymous generators!)
        self._gens2names = {}
        self._names2gens = {}

    def __len__(self):
        return len(self._gens2names)

    def __iter__(self):
        """
        Iterate over the tohu generators in this namespace.
        """
        yield from self._gens2names.keys()

    def __getitem__(self, name):
        if not isinstance(name, str):
            raise ValueError("Name of the generator must be a string. Got: {type(name)}")
        return self._names2gens[name]

    def add_with_name(self, g, name):
        assert isinstance(g, TohuBaseGenerator)
        assert isinstance(name, str)

        try:
            existing_name = self._gens2names[g]
            if existing_name is None:
                raise TohuNamespaceError(
                    "Trying to add generator with name which was previously added anonymously. "
                    "This is currently not allowed.")
            elif name != existing_name:
                raise TohuNamespaceError(f"Generator already exists with a different name. Existing name: {existing_name}")
            else:
                logger.debug("Not adding generator to namespace because it already exists with the same name.")
        except KeyError:
            # generator does not exist yet
            self._gens2names[g] = name
            self._names2gens[name] = g

    def add_anonymously(self, g):
        if g in self._gens2names:
            logger.debug("Not adding generator anonymously because it already exists with an explicit name.")
        else:
            self._gens2names[g] = None
