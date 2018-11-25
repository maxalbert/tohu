from bidict import bidict

from .base import TohuBaseGenerator
from .logging import logger


class TohuNamespaceError(Exception):
    """
    Custom exception for TohuNamespace.
    """


def get_anonymous_name_for(g):
    """
    Return a string that can be used as an anonymous name in a tohu namespace.
    """
    if g.tohu_name is not None:
        return f"ANONYMOUS_ANONYMOUS_ANONYMOUS_{g.tohu_name}"
    else:
        return f"ANONYMOUS_ANONYMOUS_ANONYMOUS_{g.tohu_id}"



class TohuNamespace:

    def __init__(self):
        self.generators = bidict()

    @property
    def names(self):
        return list(self.generators.keys())

    def __len__(self):
        return len(self.generators)

    def __iter__(self):
        yield from self.generators.keys()

    def __getitem__(self, name):
        return self.generators[name]

    def add_generator(self, g, name):
        """
        Add generator `g` to namespace under the given name.
        """
        assert isinstance(g, TohuBaseGenerator)

        name = name or get_anonymous_name_for(g)

        if g in self.generators.inv:
            existing_name = self.generators.inv[g]
            if name == existing_name:
                logger.debug(f"Not adding generator to namespace because it already exists with the same name: {g}")
            else:
                raise TohuNamespaceError("Cannot add generator because it already exists with a different name: {g} "
                                         "(existing name: {existing_name}")

        self.generators[name] = g