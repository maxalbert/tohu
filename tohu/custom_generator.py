import re
import sys
from collections import namedtuple
from mako.template import Template
from random import Random
from tqdm import tqdm

from tohu.generators import BaseGenerator

__all__ = ["CustomGenerator"]


def make_range(N, progressbar):
    if progressbar:
        return tqdm(range(N))
    else:
        return range(N)


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


def make_formatter(fmt_templates, sep, end="\n"):
    """
    Return a function which, when given a namedtuple instance as an argument,
    returns a string containing the concatenation of all its field values.
    """
    template = Template(sep.join(fmt_templates.values()) + end)

    def format_item(item, _):
        return template.render(**item._asdict())

    return format_item


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
            if self._format_dict is None:
                self._format_dict = {name: "${" + name + "}" for name in self.field_gens}
            if self._separator is None:
                self._separator = ","
            self._reinit_item_formatter()
            self.seed_generator = SeedGenerator()

            self.reset(seed)

        gen_cls.__init__ = gen_init
        return gen_cls


class CustomGenerator(BaseGenerator, metaclass=CustomGeneratorMeta):
    _format_dict = None
    _separator = None
    _header = None

    @property
    def FMT_FIELDS(self):
        return self._format_dict

    @FMT_FIELDS.setter
    def FMT_FIELDS(self, value):
        self._format_dict = value
        self._reinit_item_formatter()

    @property
    def SEPARATOR(self):
        return self._separator

    @SEPARATOR.setter
    def SEPARATOR(self, value):
        self._separator = value
        self._reinit_item_formatter()

    @property
    def HEADER(self):
        if self._header is not None:
            return self._header
        else:
            return "#" + self._separator.join(self._format_dict.keys()) + "\n"

    @HEADER.setter
    def HEADER(self, value):
        self._header = value + "\n"

    def _reinit_item_formatter(self):
        self.item_cls.__format__ = make_formatter(fmt_templates=self._format_dict, sep=self._separator, end="\n")

    def reset(self, seed=None):
        """
        Reset generator using the given seed (unless seed is None, in which case this is a no-op).
        """
        # Reset the seed generator
        self.seed_generator.seed(seed)

        # Reset each constituent generator with a new seed
        # produced by the seed generator.
        for g, x in zip(self.field_gens.values(), self.seed_generator):
            g.reset(x)

    def __next__(self):
        field_values = [next(g) for g in self.field_gens.values()]
        return self.item_cls(*field_values)

    def export(self, f, *, N, seed=None, mode='w', header=False, progressbar=True):
        assert mode in ['w', 'a', 'write', 'append'], "Argument 'mode' must be either 'w'/'write' or 'a'/'append'."

        file = open(f, mode) if isinstance(f, str) else f

        self.reset(seed)

        if isinstance(header, str):
            header = header + "\n"
        elif header is True:
            header = self.HEADER
        else:
            assert header is False

        if mode == 'w' and header is not False:
            file.write(header)

        for i in make_range(N, progressbar):
            file.write(format(next(self)))

        if isinstance(f, str):
            file.close()