from ..base import TohuBaseGenerator
from .utils import make_tohu_items_class, get_tohu_items_name

__all__ = ['CustomGenerator']


class CustomGenerator(TohuBaseGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.orig_args = args
        self.orig_kwargs = kwargs

        self._extract_constituent_generator_templates()
        self._extract_constituent_generators()
        self._set_field_names()
        self._set_tohu_items_name()
        self._set_tohu_items_cls()

    def _extract_constituent_generator_templates(self):
        """
        Set the `constituent_generator_templates` attribute to a dictionary
        of the form `{name: constituen_generator}` which contains all tohu
        generators defined in the class and instance namespaces of
        this custom generator.
        """
        gen_templates = {}

        # Extract constituent generators from class dict
        for name, g in self.__class__.__dict__.items():
            if isinstance(g, TohuBaseGenerator):
                gen_templates[name] = g.set_tohu_name(f'{name} (TPL)')

        # Extract constituent generators from instance dict
        for name, g in self.__dict__.items():
            if isinstance(g, TohuBaseGenerator):
                gen_templates[name] = g.set_tohu_name(f'{name} (TPL)')

        self.constituent_generator_templates = gen_templates

    def _extract_constituent_generators(self):
        self.constituent_generators = {name: gen.spawn() for name, gen in self.constituent_generator_templates.items()}

    def _set_field_names(self):
        constituent_generator_names = list(self.constituent_generators.keys())

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
        field_values = {name: next(self.constituent_generators[name]) for name in self.field_names}
        return self.tohu_items_cls(**field_values)

    def reset(self, seed):
        super().reset(seed)
        for gen in self.constituent_generators.values():
            gen.reset(next(self.seed_generator))
        return self

    def spawn(self):
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

        # TODO: should also set random state for anonymous/implicit constituent generators
        #        (these can occur in chains of derived generators)
        for name in self.constituent_generators.keys():
            self.constituent_generators[name]._set_random_state_from(other.constituent_generators[name])
