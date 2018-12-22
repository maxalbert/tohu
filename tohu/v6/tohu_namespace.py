from .base import TohuBaseGenerator


class TohuNamespaceError(Exception):
    pass


class TohuNamespace:

    def __init__(self):
        self._ns_named = {}
        self._ns_anonymous = []

    def __len__(self):
        return len(self._ns_named) + len(self._ns_anonymous)

    def __iter__(self):
        yield from self._ns_named.values()
        yield from self._ns_anonymous

    def __getitem__(self, name):
        return self._ns_named[name]

    def add_with_name(self, g, name):
        assert isinstance(g, TohuBaseGenerator)
        self._ns_named[name] = g

    def add_anonymously(self, g):
        self._ns_anonymous.append(g)