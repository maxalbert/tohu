from .base import TohuBaseGenerator


class TohuNamespaceError:
    """
    Custom exception for TohuNamespace
    """


class TohuNamespace:

    def __init__(self):
        self._ns = {}

    def __len__(self):
        return len(self._ns)

    def __setitem__(self, name, g):
        assert isinstance(g, TohuBaseGenerator)
        self._ns[g] = name

    @property
    def all_generators(self):
        return self._ns