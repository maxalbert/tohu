from .base import TohuBaseGenerator


class TohuNamespace:

    def __init__(self):
        self.generators = {}

    def __iter__(self):
        yield from self.generators.keys()

    def __getitem__(self, name):
        return self.generators[name]

    def add_generator(self, g, name):
        """
        Add generator `g` to namespace under the given name.
        """
        assert isinstance(g, TohuBaseGenerator)

        self.generators[name] = g