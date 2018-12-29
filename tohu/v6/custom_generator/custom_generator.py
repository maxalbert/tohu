from ..base import TohuBaseGenerator
from ..tohu_namespace import TohuNamespace
from .utils import make_tohu_items_class, get_tohu_items_name

__all__ = ['CustomGenerator']


class CustomGenerator(TohuBaseGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.orig_args = args
        self.orig_kwargs = kwargs

        self.ns_gen_templates = TohuNamespace()
        self.ns_gen_templates.update_from_dict(self.__class__.__dict__)
        self.ns_gen_templates.update_from_dict(self.__dict__)
        # self.ns_gens = TohuNamespace.from_dict({name: gen.spawn() for name, gen in self.ns_gen_templates.items()})
        self.ns_gens = self.ns_gen_templates.spawn()

        self._update_namespace_with_field_generators()
        self._add_TPL_suffix_to_field_generator_template_tohu_names()
        self._set_field_names()
        self._set_tohu_items_name()
        self._set_tohu_items_cls()

    def _add_TPL_suffix_to_field_generator_template_tohu_names(self):
        """
        Add the suffix ' (TPL)' to the tohu_names of field generator templates.
        This is purely convenience for easier debugging.
        """
        for g in self.ns_gen_templates.all_generators:
            g.set_tohu_name(f"{g.tohu_name} (TPL)")

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
