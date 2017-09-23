import re
from mako.template import Template
from collections import namedtuple
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


def make_formatter(fmt_templates, sep, end="\n"):
    """
    Return a function which, when given a namedtuple instance as an argument,
    returns a string containing the concatenation of all its field values.
    """
    template = Template(sep.join(fmt_templates.values()) + end)

    def format_item(item, _):
        return template.render(**item._asdict())

    return format_item

class CustomGenerator:
    _format_dict = None
    _separator = None

    def __init__(self, seed=None):
        clsname = get_item_class_name(self.__class__.__name__)
        clsdict = self.__class__.__dict__
        self.field_gens = {name: gen for name, gen in clsdict.items() if isinstance(gen, BaseGenerator)}
        self.item_cls = namedtuple(clsname, self.field_gens.keys())
        if self._format_dict is None:
            self._format_dict = {name: "${" + name + "}" for name in self.field_gens}
        if self._separator is None:
            self._separator = ","
        self._reinit_item_formatter()
        self.reset(seed)

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

    def _reinit_item_formatter(self):
        self.item_cls.__format__ = make_formatter(fmt_templates=self._format_dict, sep=self._separator, end="\n")

    def reset(self, seed=None):
        if seed is not None:
            for g in self.field_gens.values():
                g.reset(seed)

    def __next__(self):
        field_values = [next(g) for g in self.field_gens.values()]
        return self.item_cls(*field_values)