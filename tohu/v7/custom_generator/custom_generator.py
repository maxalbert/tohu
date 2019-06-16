from ..base import TohuBaseGenerator
from .tohu_items_class import make_tohu_items_class
from .tohu_namespace import TohuNamespace

__all__ = ["CustomGenerator"]


class CustomGenerator(TohuBaseGenerator):
    def __init__(self):
        super().__init__()
        self.ns = TohuNamespace("Quux")  # FIXME: derive this from the generator name or the __tohu_name__ attribute
        self.tohu_items_cls = None
        self.tohu_items_cls_name = None

    def __next__(self):
        return self.tohu_items_cls(**next(self.ns))

    def reset(self, seed):
        super().reset(seed)
        self.ns.reset(seed)

    def spawn(self):
        new_obj = CustomGenerator()

        # re-use existing tohu_items_cls to ensure items produced by the spawned generator are comparable with those produced by the original one
        new_obj.tohu_items_cls = self.tohu_items_cls
        new_obj.tohu_items_cls_name = self.tohu_items_cls_name

        new_obj.ns = self.ns.spawn()
        new_obj._set_state_from(self)
        return new_obj

    def _set_state_from(self, other):
        super()._set_state_from(other)

    def add_field_generator(self, name: str, generator: TohuBaseGenerator):
        """
        Parameters
        ----------
        name : str
            Field name associated with the generator.
        generator : TohuBaseGenerator
            The generator to be added.
        """
        self.ns.add_field_generator(name, generator)
        self.update_tohu_items_class()

    def set_tohu_items_class_name(self, cls_name):
        self.tohu_items_cls_name = cls_name

    def update_tohu_items_class(self):
        if self.tohu_items_cls_name is None:
            msg = "You must call `set_tohu_items_class_name` on the custom generator before adding field generators."
            raise RuntimeError(msg)
        self.tohu_items_cls = make_tohu_items_class(self.tohu_items_cls_name, self.field_names)

    @property
    def field_names(self):
        return self.ns.field_names

    @property
    def field_generators(self):
        return self.ns.field_generators
