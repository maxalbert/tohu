from ..base import SeedGenerator
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

    @property
    def field_names(self):
        return list(self._ns.keys())

    @property
    def field_generators(self):
        return self._ns.copy()

    def add_field_generator(self, name, gen):
        self._ns[name] = gen.clone()
        self.tohu_items_cls = self._get_updated_tohu_items_class()

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
        return ns_new