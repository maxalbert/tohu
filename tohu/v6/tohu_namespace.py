from .base import TohuBaseGenerator, SeedGenerator
from .logging import logger
from .spawn_mapping import SpawnMapping


class TohuNamespaceError(Exception):
    """
    Custom exception for TohuNamespace
    """


class TohuNamespace:

    def __init__(self):
        self._ns = {}
        self.seed_generator = SeedGenerator()

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
        return self._ns

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

        if g not in self._ns:
            logger.debug(f"Adding generator to namespace: {g} (name='{name}')")
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
            self._add(g, name)

    def spawn_generator(self, g, spawn_mapping, ns_spawned):
        name = self._ns[g]

        if g in ns_spawned:
            # Generator was spawned before; nothing to do
            return
        else:
            if g.parent is None:
                # Simply spawn the generator
                g_new = g.spawn(spawn_mapping)
            else:
                assert g.parent in spawn_mapping
                # Re-wire the clone
                g_new = spawn_mapping[g.parent].clone()

            spawn_mapping[g] = g_new
            ns_spawned[name] = g_new
        #
        #
        #
        # if name in ns_spawned.names:
        #     # generator was spawned before; simply return it
        #     return ns_spawned[name]
        # else:
        #     if g.parent is None:
        #         # Simply spawn the generator
        #         spawn_mapping = {"TODO TODO TODO"}
        #         ns_spawned[name] = g.spawn()
        #     else:
        #         # Re-wire clone
        #         assert g.parent in self
        #         parent_name = self._ns[g.parent]
        #         ns_spawned[name] = ns_spawned[parent_name].clone()

    def spawn(self):
        spawn_mapping = SpawnMapping()
        ns_spawned = TohuNamespace()
        for g, name in self._ns.items():
            self.spawn_generator(g, spawn_mapping, ns_spawned)
            #ns_spawned[name] = g.spawn()
        return ns_spawned

    def reset(self, seed):
        self.seed_generator.reset(seed)
        for g in self.all_generators.keys():
            g.reset(next(self.seed_generator))

    def _set_random_state_from(self, other):
        #raise NotImplementedError("TODO: Traverse the dependencies in both namespaces and transfer the state!")
        pass
