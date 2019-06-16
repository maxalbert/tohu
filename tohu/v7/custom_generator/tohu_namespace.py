from ..base import SeedGenerator, TohuBaseGenerator
from .tohu_items_class import make_tohu_items_class


class TohuNamespace:
    def __init__(self, tohu_items_cls_name):
        self._ns = {}
        self.seed_generator = SeedGenerator()
        self.tohu_items_cls_name = tohu_items_cls_name
        self.tohu_items_cls = self._get_updated_tohu_items_class()

    def __getitem__(self, name):
        return self._ns[name]

    def __next__(self):
        return self.tohu_items_cls(**{name: next(g) for name, g in self._ns.items()})

    def _set_state_from(self, other):
        assert self._ns.keys() == other._ns.keys()
        for name in self._ns.keys():
            g_self = self._ns[name]
            g_other = other._ns[name]
            g_self._set_state_from(g_other)

    @property
    def field_names(self):
        return list(self._ns.keys())

    @property
    def field_generators(self):
        return self._ns.copy()

    def find_existing_name(self, generator):
        for name, g in self._ns.items():
            if generator is g.parent:
                return name
        return None

    def add_field_generator(self, name, gen):
        self._ns[name] = gen.clone()
        self.tohu_items_cls = self._get_updated_tohu_items_class()

    def update_from_dict(self, the_dict):
        for name, gen in the_dict.items():
            if isinstance(gen, TohuBaseGenerator):
                self.add_field_generator(name, gen)

    def _get_updated_tohu_items_class(self):
        return make_tohu_items_class(self.tohu_items_cls_name, self.field_names)

    def reset(self, seed):
        self.seed_generator.reset(seed)
        for g in self._ns.values():
            g.reset(next(self.seed_generator))

    def spawn(self):
        ns_new = TohuNamespace(self.tohu_items_cls_name)
        for name, g in self._ns.items():
            ns_new.add_field_generator(name, g.parent)
        ns_new._set_state_from(self)
        return ns_new
