import logging
from .base import TohuBaseGenerator

__all__ = ['CustomGenerator']

logger = logging.getLogger('tohu')


class CustomGenerator(TohuBaseGenerator):

    def __init__(self, *args, **kwargs):
        self.orig_args = args
        self.orig_kwargs = kwargs

        self.field_gen_templates = {}

        for name, g in self.__class__.__dict__.items():
            logger.warning(f'{name}={g}')
            if isinstance(g, TohuBaseGenerator):
                self.field_gen_templates[name] = g

        self.field_gens = {name: g.spawn() for (name, g) in self.field_gen_templates.items()}

    def __next__(self):
        pass

    def reset(self, seed):
        pass

    def spawn(self):
        return self.__class__(*self.orig_args, **self.orig_kwargs)