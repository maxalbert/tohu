import re

from .base import TohuBaseGenerator
from .logging import logger
from .utils import make_tohu_item_class

__all__ = ['CustomGenerator']


class CustomGenerator(TohuBaseGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.orig_args = args
        self.orig_kwargs = kwargs

        self._extract_field_generator_templates()
        self._extract_field_generators()
        self._set_field_names()

        self._set_item_class()

    def _extract_field_generator_templates(self):
        """
        Set the `field_generator_templates` attribute to a dictionary
        of the form `{name: field_generator}` which contains all tohu
        generators defined in the class and instance namespaces of
        this custom generator.
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

        self.field_generator_templates = field_gen_templates

    def _extract_field_generators(self):
        self.field_generators = {name: gen.spawn() for name, gen in self.field_generator_templates.items()}

    def _set_field_names(self):
        field_gen_names = list(self.field_generators.keys())

        if hasattr(self, '__fields__'):
            self.field_names = self.__fields__

            # sanity check
            for field_name in self.field_names:
                if field_name not in field_gen_names:
                    raise ValueError(f"Attribute __fields__ contains name which is not a named field generator: '{field_name}'")
        else:
            self.field_names = field_gen_names

    @classmethod
    def _set_tohu_items_name(cls):
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
                msg = (
                    "Cannot derive class name for items to be produced by custom generator. "
                    "Please set '__tohu_items_name__' at the top of the custom generator's "
                    "definition or change its name so that it ends in '...Generator'"
                )
                raise ValueError(msg)

    def _set_item_class(self):
        """
        cls:
            The custom generator class for which to create an item-class
        """
        self._set_tohu_items_name()
        self.tohu_item_cls = make_tohu_item_class(self.__tohu_items_name__, self.field_names)

    def __next__(self):
        field_values = [next(g) for g in self.field_generators.values()]
        return self.tohu_item_cls(*field_values)

    def reset(self, seed):
        super().reset(seed)
        for gen in self.field_generators.values():
            gen.reset(next(self.seed_generator))

    def spawn(self):
        new_obj = self.__class__(*self.orig_args, **self.orig_kwargs)
        new_obj._set_random_state_from(self)

        # Explicitly set item_cls. This is necessary because due to
        # the way in which `attr` works, explicit comparisons between
        # generated items will return False even though they contain
        # the same elements (because the underlying attr classes are
        # different, so attr plays it safe).
        new_obj.tohu_item_cls = self.tohu_item_cls

        return new_obj

    def _set_random_state_from(self, other):
        self.seed_generator._set_random_state_from(other.seed_generator)

        # TODO: should also set random state for unnamed field generators
        #        (these can occur in chains of derived generators)
        for name in self.field_generators.keys():
            self.field_generators[name]._set_random_state_from(other.field_generators[name])
