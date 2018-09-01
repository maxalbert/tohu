import logging
from .generators import BaseGenerator

#
# Create debug logger
#
logger = logging.getLogger('tohu-debug')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('{levelname}  {message}', datefmt='%Y-%m-%d %H:%M:%S', style='{')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel('INFO')


def debug_print_dict(d, name=None):
    if name is not None:
        logger.debug(f'{name}:')
    for name, gen in d.items():
        logger.debug(f'   {name}: {gen}')


class DummyGenerator(BaseGenerator):
    """
    Dummy generator independent of all existing generators
    which we can add to a CustomGenerator v2.
    """

    def __init__(self, name, spawned_from=None):
        self.cnt = 0
        self.name = name
        self.spawned_from = spawned_from

    def __repr__(self):
        descr = f' (id={id(self)})' if self.spawned_from is None else f' (spawned from {id(self.spawned_from)})'
        return f"<DummyGenerator: '{self.name}'{descr}>"

    def _spawn(self):
        return DummyGenerator(self.name, spawned_from=self)

    def reset(self, seed=None):
        self.cnt = 0

    def __next__(self):
        value = self.cnt
        self.cnt += 1
        return f"<dummy_value: {value}>"
