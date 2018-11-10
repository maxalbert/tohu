import hashlib
from abc import ABCMeta, abstractmethod

from .logging import logger


class TohuBaseGenerator(metaclass=ABCMeta):
    """
    Base class for all of tohu's generators.
    """

    def __init__(self):
        self.tohu_name = None

    def __repr__(self):
        clsname = self.__class__.__name__
        name = '' if self.tohu_name is None else f'{self.tohu_name}: '
        return f'<{name}{clsname} (id={self.tohu_id})>'

    def __format__(self, fmt):
        return self.__repr__()

    def set_tohu_name(self, tohu_name):
        """
        Set this generator's `tohu_name` attribute.

        This is mainly useful for debugging where one can temporarily
        use this at the end of generator definitions to set a name
        that will be displayed in debugging messages. For example:

            g1 = SomeGeneratorClass().set_tohu_name('g1')
            g2 = SomeGeneratorClass().set_tohu_name('g2')
        """
        self.tohu_name = tohu_name
        return self

    @property
    def tohu_id(self):
        """
        Return (truncated) md5 hash representing this generator.
        We truncate the hash simply for readability, as this is
        purely intended for debugging purposes and the risk of
        any collisions will be negligible.
        """
        myhash = hashlib.md5(str(id(self)).encode()).hexdigest()
        return myhash[:12]

    @abstractmethod
    def reset(self, seed):
        logger.debug(f'Resetting {self} (seed={seed})')

        # TODO: reset clones once we have added them back in