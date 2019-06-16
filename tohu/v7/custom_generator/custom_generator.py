from abc import ABCMeta

from ..base import TohuBaseGenerator
from .tohu_namespace import TohuNamespace

__all__ = ["CustomGenerator"]


def augment_init_method(cls):
    """
    Replace the existing cls.__init__() method with a new one which
    also initialises the field generators and similar bookkeeping.
    """

    orig_init = cls.__init__

    def new_init(self, *args, **kwargs):
        super(cls, self).__init__()  # TODO: does this behave correctly with longer inheritance chains? I think so...(?)

        orig_init(self, *args, **kwargs)
        self.ns.update_from_dict(self.__class__.__dict__)
        self.ns.update_from_dict(self.__dict__)

    cls.__init__ = new_init



class CustomGeneratorMeta(ABCMeta):

    def __new__(metacls, cg_name, bases, clsdict):
        # Create new custom generator class
        new_cls = super(CustomGeneratorMeta, metacls).__new__(metacls, cg_name, bases, clsdict)

        # Augment original init method with bookkeeping needed for custom generators
        augment_init_method(new_cls)

        return new_cls


class CustomGenerator(TohuBaseGenerator, metaclass=CustomGeneratorMeta):
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
        self.ns._set_state_from(other.ns)  # TODO: this duplicates functionality that's already in self.ns.spawn()

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