import attr
import pandas as pd
import re

from .base import TohuBaseGenerator, SeedGenerator
from .logging import logger
from .spawn_context import SpawnContext

__all__ = ['CustomGenerator']


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
        logger.debug(f"Using item class name '{cls.__tohu_items_name__}' (derived from attribute '__tohu_items_name__')")
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
        self.field_gen_templates = self._find_field_generator_templates()

        spawn_context = SpawnContext()
        for name, g in self.field_gen_templates.items():
            spawn_context.spawn_template(g, name=name)

        self.field_gens_named = spawn_context.named_spawns
        self.field_gens_all = spawn_context.spawns

        self.__dict__.update(self.field_gens_named)

        set_item_class_name_on_custom_generator_class(self.__class__)
        self._set_field_names_and_field_gens()
        self._set_item_class()

    def _set_field_names_and_field_gens(self):
        field_gen_names = list(self.field_gens_named.keys())

        if hasattr(self, '__fields__'):
            self.field_names = self.__fields__
        else:
            self.field_names = field_gen_names

        if hasattr(self, '__fields__'):
            # sanity check
            for field_name in self.field_names:
                if field_name not in field_gen_names:
                    raise ValueError(f"Attribute __fields__ contains name which is not a named field generator: '{field_name}'")

        self.field_gens = {name: gen for (name, gen) in self.field_gens_named.items() if name in self.field_names}

    def _set_item_class(self):
        """
        cls:
            The custom generator class for which to create an item-class
        """
        clsname = self.__tohu_items_name__
        self.item_cls = make_item_class(clsname, self.field_names)

    def __next__(self):
        field_values = [next(g) for g in self.field_gens.values()]
        return self.item_cls(*field_values)

    def _find_field_generator_templates(self):
        """
        Return a dictionary of the form {name: field_generator} containing
        all tohu generators defined in the class and instance namespace
        of this custom generator.
        """
        field_gen_templates = {}

        # Extract field generators from class dict
        for name, g in self.__class__.__dict__.items():
            if isinstance(g, TohuBaseGenerator):
                field_gen_templates[name] = g.set_tohu_name(f'{name} (TPL)')

        # Extract field generators from instance dict
        for name, g in self.__dict__.items():
            if isinstance(g, TohuBaseGenerator):
                field_gen_templates[name] = g.set_tohu_name(f'{name} (TPL)')

        return field_gen_templates

    def reset(self, seed):
        super().reset(seed)
        self.seed_generator.reset(seed)
        for name, gen in self.field_gens_all.items(): # FIXME: reset all field gens
            next_seed = next(self.seed_generator)
            gen.reset(next_seed)
        return self

    def spawn(self):
        new_obj = self.__class__(*self.orig_args, **self.orig_kwargs)
        new_obj._set_random_state_from(self)

        # Explicitly set item_cls. This is necessary because due to
        # the way in which `attr` works, explicit comparisons between
        # generated items will return False even though they contain
        # the same elements (because the underlying attr classes are
        # different, so attr plays it safe).
        new_obj.item_cls = self.item_cls

        return new_obj

    def _set_random_state_from(self, other):
        self.seed_generator._set_random_state_from(other.seed_generator)

        # FIXME: should also set random state for unnamed field generators
        #        (these can occur in chains of derived generators)
        for name in self.field_gens_all.keys():
            self.field_gens_all[name]._set_random_state_from(other.field_gens_all[name])
