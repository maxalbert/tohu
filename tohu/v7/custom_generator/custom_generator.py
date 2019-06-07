from ..base import TohuBaseGenerator
from .tohu_items_class import make_tohu_items_class

__all__ = ["make_new_custom_generator"]


class CustomGenerator:
    def __init__(self):
        self.field_generators = {}
        self.tohu_items_cls = None

    def add_field_generator(self, name: str, generator: TohuBaseGenerator):
        """
        Parameters
        ----------
        name : str
            Field name associated with the generator.
        generator : TohuBaseGenerator
            The generator to be added.
        """
        self.field_generators[name] = generator.clone()

    def make_tohu_items_class(self, cls_name):
        self.tohu_items_cls = make_tohu_items_class(cls_name, self.fields)

    @property
    def fields(self):
        """
        Return
        """
        return list(self.field_generators.keys())


def make_new_custom_generator():
    return CustomGenerator()
