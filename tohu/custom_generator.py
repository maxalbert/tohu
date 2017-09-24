import re
import sys
from collections import namedtuple
from mako.template import Template
from random import Random
from tqdm import tqdm

from tohu.generators import BaseGenerator

__all__ = ["CustomGenerator"]


def get_item_class_name(generator_class_name):
    """
    Given the name of a generator class (such as "FoobarGenerator),
    return the first part of the name before "Generator", which
    will be used for the namedtuple items produced by this generator.

    Examples:
        FoobarGenerator -> Foobar
        QuuxGenerator   -> Quux
    """
    return re.match('^(.*)Generator$', generator_class_name).group(1)


class SeedGenerator:
    """
    This class is used in custom generators to create a collection of
    seeds when reset() is called, so that each of the constituent
    generators can be re-initialised with a different seed in a
    reproducible way.

    Note: This is almost identical to the `Integer` class above, but
    we need a version which does *not* inherit from `BaseGenerator`,
    otherwise the automatic namedtuple creation in `CustomGeneratorMeta`
    gets confused.
    """

    def __init__(self):
        self.r = Random()
        self.minval = 0
        self.maxval = sys.maxsize

    def seed(self, value):
        self.r.seed(value)

    def __iter__(self):
        return self

    def __next__(self):
        return self.r.randint(self.minval, self.maxval)


class CustomGeneratorMeta(type):
    def __new__(metacls, cg_name, bases, clsdict):
        gen_cls = super(CustomGeneratorMeta, metacls).__new__(metacls, cg_name, bases, clsdict)
        orig_init = gen_cls.__init__

        def gen_init(self, *args, **kwargs):
            seed = kwargs.pop('seed', None)

            # Call original __init__ function to make sure all generator attributes are defined
            orig_init(self, *args, **kwargs)

            clsdict = self.__class__.__dict__
            instdict = self.__dict__
            self.field_gens = {name: gen._spawn() for name, gen in dict(**clsdict, **instdict).items() if isinstance(gen, BaseGenerator)}
            clsname = get_item_class_name(self.__class__.__name__)
            self.item_cls = namedtuple(clsname, self.field_gens.keys())
            self.seed_generator = SeedGenerator()
            self.reset(seed)

        gen_cls.__init__ = gen_init
        return gen_cls


class CustomGenerator(BaseGenerator, metaclass=CustomGeneratorMeta):

    def reset(self, seed=None):
        """
        Reset generator using the given seed (unless seed is None, in which case this is a no-op).
        """
        # Reset the seed generator
        if seed is not None:
            self.seed_generator.seed(seed)

            # Reset each constituent generator with a new seed
            # produced by the seed generator.
            for g, x in zip(self.field_gens.values(), self.seed_generator):
                g.reset(x)

    def __next__(self):
        field_values = [next(g) for g in self.field_gens.values()]
        return self.item_cls(*field_values)
