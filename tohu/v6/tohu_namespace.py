from .base import TohuBaseGenerator


class TohuNamespace:

    def __init__(self):
        self.generators = {}

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

        name = name or f"ANONYMOUS_ANONYMOUS_ANONYMOUS_{g.tohu_id}"
        self.generators[name] = g