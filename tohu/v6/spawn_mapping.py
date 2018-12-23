from .logging import logger


class SpawnMapping:
    def __init__(self):
        self.mapping = dict()

    def __contains__(self, g):
        return g in self.mapping.keys()

    def __setitem__(self, g, g_spawned):
        self.mapping[g] = g_spawned

    def __getitem__(self, g):
        try:
            return self.mapping[g]
        except KeyError:
            logger.warning(f"Generator does not occur in spawn mapping: {g}")
            return g