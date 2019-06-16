from ..base import TohuBaseGenerator
from .tohu_namespace import TohuNamespace

__all__ = ["CustomGenerator"]


class CustomGenerator(TohuBaseGenerator):
    def __init__(self, tohu_items_name=None):
        super().__init__()
        tohu_items_name = tohu_items_name or self._get_tohu_items_name()
        self.ns = TohuNamespace(tohu_items_name)

    def __next__(self):
        return next(self.ns)

    def reset(self, seed):
        super().reset(seed)
        self.ns.reset(seed)

    def spawn(self):
        new_obj = CustomGenerator()
        new_obj.ns = self.ns.spawn()
        new_obj._set_state_from(self)
        return new_obj

    def _set_state_from(self, other):
        super()._set_state_from(other)
        # TODO: set state of generators in namespace!

    def _get_tohu_items_name(self):
        return "Quux"  # FIXME: derive this from the generator name or the __tohu_name__ attribute

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

    @property
    def field_names(self):
        return self.ns.field_names

    @property
    def field_generators(self):
        return self.ns.field_generators

    @property
    def tohu_items_cls(self):
        return self.ns.tohu_items_cls

    @tohu_items_cls.setter
    def tohu_items_cls(self, value):
        pass