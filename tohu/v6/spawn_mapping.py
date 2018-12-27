from .logging import logger


class SpawnMapping:
    def __init__(self):
        self.mapping = dict()

    def __repr__(self):
        return f"<SpawnMapping: {self.mapping}>"

    def __contains__(self, g):
        return g in self.mapping.keys()

    def __setitem__(self, g, g_spawned):
        self.mapping[g] = g_spawned

    def __getitem__(self, g):
        try:
            return self.mapping[g]
        except KeyError:
            logger.debug(f"Generator does not occur in spawn mapping: {g}. Returning it unchanged.")
            return g