from abc import ABCMeta
from ..base import TohuBaseGenerator
from ..tohu_namespace import TohuNamespace
from .utils import make_tohu_items_class, get_tohu_items_name

__all__ = ['CustomGenerator']


def augment_init_method(cls):
    """
    Replace the existing cls.__init__() method with a new one which
    also initialises the field generators and similar bookkeeping.
    """

    orig_init = cls.__init__

    def new_init(self, *args, **kwargs):
        super(CustomGenerator, self).__init__()  # TODO: does this behave correctly with longer inheritance chains?

        orig_init(self, *args, **kwargs)

        self.orig_args = args
        self.orig_kwargs = kwargs

        self.ns_gen_templates = TohuNamespace()
        self.ns_gen_templates.update_from_dict(self.__class__.__dict__)
        self.ns_gen_templates.update_from_dict(self.__dict__)
        self.ns_gen_templates.set_owner(self.__class__)
        self._mark_field_generator_templates()

        self.ns_gens = self.ns_gen_templates.spawn()
        self.ns_gens.set_owner(self)

        self._update_namespace_with_field_generators()
        self._set_field_names()
        self._set_tohu_items_name()
        self._set_tohu_items_cls()

    cls.__init__ = new_init


class CustomGeneratorMeta(ABCMeta):

    def __new__(metacls, cg_name, bases, clsdict):
        # Create new custom generator class
        new_cls = super(CustomGeneratorMeta, metacls).__new__(metacls, cg_name, bases, clsdict)

        # Augment original init method with bookkeeping needed for custom generators
        augment_init_method(new_cls)

        return new_cls


class CustomGenerator(TohuBaseGenerator, metaclass=CustomGeneratorMeta):

    def _mark_field_generator_templates(self):
        """
        Mark field generator templates as such so that an indication of this is
        included in the tohu_name. This is purely convenience for easier debugging.
        """
        for g in self.ns_gen_templates.all_generators:
            g.is_custom_generator_template = True

    def _update_namespace_with_field_generators(self):
        self.__dict__.update(self.ns_gens.named_generators)

    def _set_field_names(self):
        constituent_generator_names = list(self.ns_gens.names)

        if not hasattr(self, '__fields__'):
            self.field_names = constituent_generator_names
        else:
            self.field_names = self.__fields__

            # sanity check
            for field_name in self.field_names:
                if field_name not in constituent_generator_names:
                    raise ValueError(f"Attribute __fields__ contains name which is not a named field generator: '{field_name}'")

    def _set_tohu_items_name(self):
        self.__class__.__tohu_items_name__ = get_tohu_items_name(self.__class__)

    def _set_tohu_items_cls(self):
        if not hasattr(self.__class__, 'tohu_items_cls'):
            self.__class__.tohu_items_cls = make_tohu_items_class(self.__tohu_items_name__, self.field_names)

    def __next__(self):
        field_values = {name: next(self.ns_gens[name]) for name in self.field_names}
        return self.tohu_items_cls(**field_values)

    def reset(self, seed):
        super().reset(seed)
        self.ns_gens.reset(seed)
        return self

    def spawn(self, spawn_mapping=None):
        new_obj = self.__class__(*self.orig_args, **self.orig_kwargs)
        new_obj._set_random_state_from(self)

        # # Explicitly set tohu_items_cls. This is necessary because due to
        # # the way in which `attr` works, explicit comparisons between
        # # generated items will return False even though they contain
        # # the same elements (because the underlying attr classes are
        # # different, so attr plays it safe).
        # new_obj.tohu_items_cls = self.tohu_items_cls

        return new_obj

    def _set_random_state_from(self, other):
        super()._set_random_state_from(other)
        self.ns_gens._set_random_state_from(other.ns_gens)
