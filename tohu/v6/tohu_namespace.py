from itertools import count

from .base import TohuBaseGenerator, SeedGenerator
from .logging import logger
from .spawn_mapping import SpawnMapping
from .utils import is_clone


class TohuNamespaceError(Exception):
    """
    Custom exception for TohuNamespace
    """


class TohuNamespace:

    _global_count = count(start=1)

    def __init__(self):
        self._ns = {}
        self.seed_generator = SeedGenerator()
        self._idx = next(self._global_count)

    def __repr__(self):
        return f"<TohuNamespace #{self._idx}>"

    @classmethod
    def from_dict(cls, d):
        ns = TohuNamespace()
        ns.update_from_dict(d)
        return ns

    def update_from_dict(self, d):
        for name, g in d.items():
            if isinstance(g, TohuBaseGenerator):
                self[name] = g

    def __len__(self):
        return len(self._ns)

    def __contains__(self, g):
        return g in self._ns.keys()

    def to_str(self):
        s = ""
        for g, name in self._ns.items():
            prefix = "    " if name is None else f"{name}: "
            suffix = " (anonymous)" if name is None else ""
            s += f"{prefix}{g}{suffix}\n"
        return s

    @property
    def all_generators(self):
        """
        Return all generators in this namespace.
        """
        return self._ns

    @property
    def all_independent_generators(self):
        """
        Return all generators in this namespace which are not clones.
        """
        return {g: name for g, name in self._ns.items() if not is_clone(g)}

    @property
    def named_generators(self):
        return {name: g for g, name in self._ns.items() if name is not None}

    @property
    def names(self):
        return [x for x in self._ns.values() if x is not None]

    def __getitem__(self, key):
        for g, name in self._ns.items():
            if name == key:
                return g
        raise KeyError(f"No generator with name '{key}' exists in this namespace.")

    def _add(self, g, name):
        for g_input in g.input_generators:
            self._add(g_input, name=None)

        if g.parent is not None:
            self._add(g.parent, name=None)

        if g not in self._ns:
            logger.debug(f"Adding generator to {self}: {g} (name='{name}')")
            self._ns[g] = name

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
            if name in self._ns.values():
                # TODO: is keeping the existing generator and ignoring the new one the right thing to do in all cases?
                logger.debug(f"A different generator already exists with name '{name}'. Ignoring the new one.")
            else:
                self._add(g, name)

    def spawn_generator(self, g, spawn_mapping, ns_spawned):
        logger.debug(f"Spawning generator in {self}: {g}")
        name = self._ns[g]

        if g in ns_spawned:
            # Generator was spawned before; nothing to do
            return
        else:
            if g.parent is not None:
                # Re-wire the clone
                if g.parent not in spawn_mapping:
                    raise TohuNamespaceError(
                        f"The cloned generator {g} is present in the tohu namespace "
                        f"but its parent {g.parent} is not. This should never happen."
                    )
                g_new = g.clone()
                new_parent = spawn_mapping[g.parent]
                g.unregister_clone(g_new)
                g_new.register_parent(new_parent)
                new_parent.register_clone(g_new)
            else:
                # Sanity check that all input generators of g have already been spawned before.
                for g_input in g.input_generators:
                    if g_input not in spawn_mapping:
                        raise TohuNamespaceError(
                            f"Spawn mapping is missing the input generator {g_input} for generator {g}. "
                            f"This should not happen! Need to check the logic of the implementation."
                        )

                # Simply spawn the generator
                g_new = g.spawn(spawn_mapping)

            spawn_mapping[g] = g_new
            ns_spawned[name] = g_new

            # Copy tohu names for easier debugging (so that
            # a custom generator instance has the same tohu
            # names for constituent generators as the class).
            g_new.set_tohu_name(g.tohu_name)

    def spawn(self):
        spawn_mapping = SpawnMapping()
        ns_spawned = TohuNamespace()
        for g, name in self._ns.items():
            self.spawn_generator(g, spawn_mapping, ns_spawned)
            #ns_spawned[name] = g.spawn()
        return ns_spawned

    def reset(self, seed):
        self.seed_generator.reset(seed)
        for g in self.all_independent_generators:
            g.reset(next(self.seed_generator))

    def _set_random_state_from(self, other):
        # TODO: double-check that this traverses generators in both namespaces in the same order
        for g_self, g_other in zip(self._ns, other._ns):
            g_self._set_random_state_from(g_other)

    def set_owner(self, owner):
        for g in self._ns:
            g.owner = owner
