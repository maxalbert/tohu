from ..base import SeedGenerator


class TohuNamespace:

    def __init__(self):
        self._ns = {}
        self.seed_generator = SeedGenerator()

    def __getitem__(self, name):
        return self._ns[name]

    @property
    def field_names(self):
        return list(self._ns.keys())

    def add_field_generator(self, name, gen):
        self._ns[name] = gen.clone()

    def reset(self, seed):
        self.seed_generator.reset(seed)
        for g in self._ns.values():
            g.reset(next(self.seed_generator))

    def __next__(self):
        return {name: next(g) for name, g in self._ns.items()}

    def spawn(self):
        ns_new = TohuNamespace()
        for name, g in self._ns.items():
            ns_new.add_field_generator(name, g.parent)
        return ns_new