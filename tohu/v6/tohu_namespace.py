from bidict import bidict

from .base import TohuBaseGenerator, SeedGenerator
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
        self.seed_generator = SeedGenerator()

    @classmethod
    def from_dict(cls, d):
        ns = cls()
        ns.update_from_dict(d)
        return ns

    def update_from_dict(self, d):
        for name, value in d.items():
            if isinstance(value, TohuBaseGenerator):
                self.add_generator(value, name)

    def keys(self):
        return list(self.generators.keys())

    def items(self):
        return list(self.generators.items())

    @property
    def names(self):
        return [name for name, g in self.generators.items() if not self.is_anonymous(g)]

    @property
    def named_generators(self):
        return {name: self.generators[name] for name in self.names}

    def get_name(self, g):
        try:
            return self.generators.inv[g]
        except KeyError:
            raise KeyError(f"Generator not present in namespace: {g}")

    def __len__(self):
        return len(self.generators)

    def __iter__(self):
        yield from self.generators.keys()

    def __getitem__(self, name):
        return self.generators[name]

    def to_str(self):
        s = ""
        for name, g in self.generators.items():
            prefix = "    " if self.is_anonymous(g) else f"{name}: "
            suffix = " (anonymous)" if self.is_anonymous(g) else ""
            s += f"{prefix}{g}{suffix}\n"
        return s

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
            existing_name = self.get_name(g)
            if new_name == existing_name:
                logger.debug(f"Not adding generator to namespace because it already exists with the same name: {g}")
            else:
                if self.is_anonymous(g):
                    self.generators.inv[g] = new_name  # update anonymous name with explicit one
                elif name is None:
                    pass  # no update needed here (the existing name is already explicit and the new one would be anonymous)
                else:
                    raise TohuNamespaceError(
                        f"Cannot add generator {g} with new name {new_name} because it already exists with a different name: {g}. Existing name: '{existing_name}'")

    def reset(self, seed):
        self.seed_generator.reset(seed)
        for g in self.generators.values():
            g.reset(seed=next(self.seed_generator))

    def _set_random_state_from(self, other):
        assert isinstance(other, TohuNamespace)

        if self.keys() != other.keys():
            raise TohuNamespaceError("Namespaces must contain the same keys.")

        for key, g_self in self.generators.items():
            g_other = other[key]

            if type(g_self) is not type(g_other):
                raise TohuNamespaceError("Generators in both namespaces must have be of the same types.")

            g_self._set_random_state_from(g_other)