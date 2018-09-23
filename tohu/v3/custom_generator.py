import attr
import logging
import re
from .base import TohuBaseGenerator, SeedGenerator

__all__ = ['CustomGenerator']

logger = logging.getLogger('tohu')


def set_item_class_name_on_custom_generator_class(cls):
    """
    Set the attribute `cls.__tohu_items_name__` to a string which defines the name
    of the namedtuple class which will be used to produce items for the custom
    generator.

    By default this will be the first part of the class name (before '...Generator'),
    for example:

        FoobarGenerator -> Foobar
        QuuxGenerator   -> Quux

    However, it can be set explicitly by the user by defining `__tohu_items_name__`
    in the class definition, for example:

        class Quux(CustomGenerator):
            __tohu_items_name__ = 'MyQuuxItem'
    """
    if '__tohu_items_name__' in cls.__dict__:
        logger.debug(
            f"Using item class name '{cls.__tohu_items_name__}' (derived from attribute '__tohu_items_name__')")
    else:
        m = re.match('^(.*)Generator$', cls.__name__)
        if m is not None:
            cls.__tohu_items_name__ = m.group(1)
            logger.debug(f"Using item class name '{cls.__tohu_items_name__}' (derived from custom generator name)")
        else:
            raise ValueError("Cannot derive class name for items to be produced by custom generator. "
                             "Please set '__tohu_items_name__' at the top of the custom generator's "
                             "definition or change its name so that it ends in '...Generator'")


def make_item_class(clsname, attr_names):
    """
    Parameters
    ----------
    clsname: string
        Name of the class to be created

    attr_names: list of strings
        Names of the attributes of the class to be created
    """

    item_cls = attr.make_class(clsname, {name: attr.ib() for name in attr_names}, repr=False, cmp=True)

    def new_repr(self):
        all_fields = ', '.join([f'{name}={repr(value)}' for name, value in attr.asdict(self).items()])
        return f'{clsname}({all_fields})'

    orig_eq = item_cls.__eq__

    def new_eq(self, other):
        """
        Custom __eq__() method which also allows comparisons with
        tuples and dictionaries. This is mostly for convenience
        during testing.
        """

        if isinstance(other, self.__class__):
            return orig_eq(self, other)
        else:
            if isinstance(other, tuple):
                return attr.astuple(self) == other
            elif isinstance(other, dict):
                return attr.asdict(self) == other
            else:
                return NotImplemented

    item_cls.__repr__ = new_repr
    item_cls.__eq__ = new_eq
    item_cls.keys = lambda self: attr_names
    item_cls.__getitem__ = lambda self, key: getattr(self, key)
    item_cls.as_dict = lambda self: attr.asdict(self)
    item_cls.to_series = lambda self: pd.Series(attr.asdict(self))

    return item_cls


class CustomGenerator(TohuBaseGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.orig_args = args
        self.orig_kwargs = kwargs

        self.seed_generator = SeedGenerator()
        self.field_gen_templates = {}

        for name, g in self.__class__.__dict__.items():
            if isinstance(g, TohuBaseGenerator):
                self.field_gen_templates[name] = g

        # TODO: extract field generators from instance dict too

        self.field_gens = {name: g.spawn() for (name, g) in self.field_gen_templates.items()}

        set_item_class_name_on_custom_generator_class(self.__class__)
        self._set_item_class()

    def _set_item_class(self):
        """
        cls:
            The custom generator class for which to create an item-class
        """
        clsname = self.__tohu_items_name__
        attr_names = self.field_gens.keys()
        self.item_cls = make_item_class(clsname, attr_names)

    def __next__(self):
        field_values = [next(g) for g in self.field_gens.values()]
        return self.item_cls(*field_values)

    def reset(self, seed):
        super().reset(seed)
        self.seed_generator.reset(seed)
        for name, gen in self.field_gens.items():
            next_seed = next(self.seed_generator)
            gen.reset(next_seed)

    def spawn(self):
        return self.__class__(*self.orig_args, **self.orig_kwargs)