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
        return f"ANONYMOUS_ANONYMOUS_ANONYMOUS_{g.__class__.__name__}_{g.tohu_id}"


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

    def contains_generator(self, g):
        return (g in self.generators.inv)

    def is_anonymous(self, g):
        try:
            existing_name = self.generators.inv[g]
        except KeyError:
            raise TohuNamespaceError(f"Namespace does not contain generator: {g}")

        return existing_name.startswith("ANONYMOUS_ANONYMOUS_ANONYMOUS_")

    def add_generator(self, g, name):
        """
        Add generator `g` to namespace under the given name.
        """
        assert isinstance(g, TohuBaseGenerator)

        new_name = name or get_anonymous_name_for(g)

        for g_input in g.input_generators:
            self.add_generator(g_input, name=None)

        if not self.contains_generator(g):
            self.generators[new_name] = g
        else:
            existing_name = self.generators.inv[g]
            if new_name == existing_name:
                logger.debug(f"Not adding generator to namespace because it already exists with the same name: {g}")
            else:
                if self.is_anonymous(g):
                    self.generators.inv[g] = new_name  # update anonymous name with explicit one
                elif name is None:
                    pass  # no update needed here (the existing name is explicit and the new one would be anonymous)
                else:
                    raise TohuNamespaceError(
                        f"Cannot add generator {g} with new name {new_name} because it already exists with a different name: {g}. Existing name: '{existing_name}'")
