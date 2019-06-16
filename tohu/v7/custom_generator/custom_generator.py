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
        self.ns_gens.update_from_dict(self.__class__.__dict__)
        self.ns_gens.update_from_dict(self.__dict__)

    cls.__init__ = new_init


class CustomGeneratorMeta(ABCMeta):
    def __new__(metacls, cg_name, bases, clsdict):
        # Create new custom generator class
        new_cls = super(CustomGeneratorMeta, metacls).__new__(metacls, cg_name, bases, clsdict)

        # Augment original init method with bookkeeping needed for custom generators
        augment_init_method(new_cls)

        return new_cls


class CustomGeneratorImpl(TohuBaseGenerator):
    def __init__(self, tohu_items_name=None):
        super().__init__()
        tohu_items_name = tohu_items_name or self._get_tohu_items_name()
        self.ns_gens = TohuNamespace(tohu_items_name)

    def __next__(self):
        return next(self.ns_gens)

    def reset(self, seed):
        super().reset(seed)
        self.ns_gens.reset(seed)

    def spawn(self):
        new_obj = CustomGeneratorImpl()
        new_obj.ns_gens = self.ns_gens.spawn()
        new_obj._set_state_from(self)
        return new_obj

    def _set_state_from(self, other):
        super()._set_state_from(other)
        # TODO: the following line duplicates functionality in self.ns.spawn()! Can we avoid this?
        self.ns_gens._set_state_from(other.ns_gens)

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
        self.ns_gens.add_field_generator(name, generator)

    @property
    def field_names(self):
        return self.ns_gens.field_names

    @property
    def field_generators(self):
        return self.ns_gens.field_generators

    @property
    def tohu_items_cls(self):
        return self.ns_gens.tohu_items_cls

    @tohu_items_cls.setter
    def tohu_items_cls(self, value):
        # TODO: this silently ignores setting the tohu_items_cls.
        # The reason is that TohuBaseGenerator will try to set this
        # to MissingTohuItemsCls, but here in CustomGenerator we
        # of course set it ourselves. However, if there is ever a
        # legitimate reason to set this from the outside this will
        # cause a bug. Might be good to find a better way of dealing
        # with this (maybe via a property on TohuBaseGenerator?
        pass


class CustomGenerator(CustomGeneratorImpl, metaclass=CustomGeneratorMeta):
    pass